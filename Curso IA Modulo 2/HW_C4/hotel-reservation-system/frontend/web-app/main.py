"""
Frontend del Sistema de Reservaciones de Hotel
Interfaz web interactiva construida con Streamlit
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="🏨 Hotel Reservations",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CONFIGURACIÓN ====================

API_BASE_URL = "http://localhost:8000"  # API Gateway

# ==================== UTILIDADES ====================

def make_api_request(endpoint: str, method: str = "GET", data: dict = None, headers: dict = None) -> Dict[str, Any]:
    """Realizar solicitud a la API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if headers is None:
            headers = {}
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Método HTTP no soportado: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error en la API ({response.status_code}): {response.text}")
            return {"success": False, "message": "Error en la API"}
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error de conexión: {e}")
        return {"success": False, "message": "Error de conexión"}
    except Exception as e:
        st.error(f"Error inesperado: {e}")
        return {"success": False, "message": "Error inesperado"}

def get_auth_headers() -> Dict[str, str]:
    """Obtener headers de autenticación"""
    if 'access_token' in st.session_state:
        return {"Authorization": f"Bearer {st.session_state.access_token}"}
    return {}

def is_authenticated() -> bool:
    """Verificar si el usuario está autenticado"""
    return 'access_token' in st.session_state and 'user_info' in st.session_state

def logout():
    """Cerrar sesión"""
    for key in ['access_token', 'user_info']:
        if key in st.session_state:
            del st.session_state[key]

# ==================== COMPONENTES DE AUTENTICACIÓN ====================

def show_login_page():
    """Mostrar página de login"""
    st.title("🏨 Sistema de Reservaciones de Hotel")
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
    
    with tab1:
        st.subheader("Iniciar Sesión")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="usuario@ejemplo.com")
            password = st.text_input("🔒 Contraseña", type="password")
            submit_login = st.form_submit_button("🚀 Iniciar Sesión", use_container_width=True)
            
            if submit_login:
                if email and password:
                    login_data = {"email": email, "password": password}
                    response = make_api_request("/auth/login", "POST", login_data)
                    
                    if response.get("success"):
                        user_data = response["data"]
                        st.session_state.access_token = user_data["access_token"]
                        st.session_state.user_info = user_data["user"]
                        st.success("✅ Login exitoso!")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales inválidas")
                else:
                    st.warning("⚠️ Por favor completa todos los campos")
    
    with tab2:
        st.subheader("Crear Cuenta Nueva")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("👤 Nombre")
                email_reg = st.text_input("📧 Email")
                password_reg = st.text_input("🔒 Contraseña", type="password")
            
            with col2:
                last_name = st.text_input("👤 Apellido")
                phone = st.text_input("📱 Teléfono")
                confirm_password = st.text_input("🔒 Confirmar Contraseña", type="password")
            
            submit_register = st.form_submit_button("✨ Crear Cuenta", use_container_width=True)
            
            if submit_register:
                if all([first_name, last_name, email_reg, password_reg, confirm_password]):
                    if password_reg == confirm_password:
                        register_data = {
                            "first_name": first_name,
                            "last_name": last_name,
                            "email": email_reg,
                            "phone": phone,
                            "password": password_reg,
                            "confirm_password": confirm_password
                        }
                        
                        response = make_api_request("/auth/register", "POST", register_data)
                        
                        if response.get("success"):
                            st.success("✅ Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
                        else:
                            st.error("❌ Error creando la cuenta")
                    else:
                        st.error("❌ Las contraseñas no coinciden")
                else:
                    st.warning("⚠️ Por favor completa todos los campos obligatorios")

# ==================== COMPONENTES PRINCIPALES ====================

def show_dashboard():
    """Mostrar dashboard principal"""
    user_info = st.session_state.user_info
    
    # Header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title(f"🏨 Bienvenido, {user_info['first_name']}!")
    
    with col2:
        st.metric("👤 Rol", user_info['role'].title())
    
    with col3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
            st.rerun()
    
    st.markdown("---")
    
    # Navegación por pestañas
    tabs = st.tabs([
        "🔍 Buscar Habitaciones",
        "📋 Mis Reservas", 
        "💳 Pagos",
        "🔔 Notificaciones"
    ])
    
    # Agregar pestañas de administración si es admin
    if user_info['role'] in ['admin', 'hotel_manager']:
        tabs.extend([
            "🏨 Gestión Hoteles",
            "🛏️ Gestión Habitaciones",
            "📊 Analytics"
        ])
    
    with tabs[0]:
        show_room_search()
    
    with tabs[1]:
        show_my_reservations()
    
    with tabs[2]:
        show_payments()
    
    with tabs[3]:
        show_notifications()
    
    # Pestañas de administración
    if user_info['role'] in ['admin', 'hotel_manager']:
        with tabs[4]:
            show_hotel_management()
        
        with tabs[5]:
            show_room_management()
        
        with tabs[6]:
            show_analytics()

def show_room_search():
    """Mostrar búsqueda de habitaciones"""
    st.subheader("🔍 Buscar Habitaciones Disponibles")
    
    # Formulario de búsqueda
    with st.form("search_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            city = st.text_input("🏙️ Ciudad", placeholder="Ej: Madrid")
            check_in = st.date_input("📅 Check-in", value=date.today() + timedelta(days=1))
        
        with col2:
            guests = st.number_input("👥 Huéspedes", min_value=1, max_value=10, value=2)
            check_out = st.date_input("📅 Check-out", value=date.today() + timedelta(days=2))
        
        with col3:
            room_type = st.selectbox("🛏️ Tipo de Habitación", 
                                   ["", "single", "double", "twin", "triple", "suite", "presidential", "family"])
            max_price = st.number_input("💰 Precio máximo por noche", min_value=0, value=500)
        
        search_button = st.form_submit_button("🔍 Buscar", use_container_width=True)
    
    if search_button:
        # Preparar parámetros de búsqueda
        search_params = {
            "check_in_date": check_in.isoformat(),
            "check_out_date": check_out.isoformat(),
            "guests": guests
        }
        
        if city:
            search_params["city"] = city
        if room_type:
            search_params["room_type"] = room_type
        if max_price > 0:
            search_params["max_price"] = max_price
        
        # Realizar búsqueda
        response = make_api_request("/rooms/search", "GET", search_params)
        
        if response.get("success"):
            rooms = response.get("data", [])
            
            if rooms:
                st.success(f"✅ Se encontraron {len(rooms)} habitaciones disponibles")
                
                # Mostrar resultados
                for i, room_data in enumerate(rooms):
                    room = room_data["room"]
                    hotel = room_data["hotel"]
                    total_price = room_data["total_price"]
                    nights = room_data["nights"]
                    
                    with st.expander(f"🏨 {hotel['name']} - Habitación {room['room_number']} (${total_price:.2f})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**🛏️ Tipo:** {room['room_type'].title()}")
                            st.write(f"**👥 Capacidad:** {room['capacity']} personas")
                            st.write(f"**📍 Ubicación:** {hotel['address']}, {hotel['city']}")
                            st.write(f"**💰 Precio por noche:** ${room['price_per_night']:.2f}")
                            st.write(f"**🌟 Rating:** {hotel.get('rating', 'N/A')}/5")
                            
                            if room.get('description'):
                                st.write(f"**📝 Descripción:** {room['description']}")
                        
                        with col2:
                            st.write(f"**📊 Total: ${total_price:.2f}**")
                            st.write(f"**🌙 {nights} noches**")
                            
                            if st.button(f"📋 Reservar", key=f"book_{i}", use_container_width=True):
                                create_reservation(room['id'], hotel['id'], check_in, check_out, guests)
            else:
                st.info("ℹ️ No se encontraron habitaciones disponibles con esos criterios")
        else:
            st.error("❌ Error en la búsqueda")

def create_reservation(room_id: str, hotel_id: str, check_in: date, check_out: date, guests: int):
    """Crear nueva reserva"""
    st.subheader("📋 Crear Reserva")
    
    with st.form("reservation_form"):
        st.write("**Detalles de la reserva:**")
        st.write(f"📅 Check-in: {check_in}")
        st.write(f"📅 Check-out: {check_out}")
        st.write(f"👥 Huéspedes: {guests}")
        
        special_requests = st.text_area("📝 Solicitudes especiales", 
                                      placeholder="Ej: Cama extra, vista al mar, etc.")
        
        confirm_button = st.form_submit_button("✅ Confirmar Reserva", use_container_width=True)
        
        if confirm_button:
            reservation_data = {
                "hotel_id": hotel_id,
                "room_id": room_id,
                "check_in_date": check_in.isoformat(),
                "check_out_date": check_out.isoformat(),
                "guests": guests,
                "special_requests": special_requests
            }
            
            headers = get_auth_headers()
            response = make_api_request("/reservations", "POST", reservation_data, headers)
            
            if response.get("success"):
                reservation = response["data"]
                st.success("✅ ¡Reserva creada exitosamente!")
                st.info(f"📋 Código de confirmación: **{reservation['confirmation_code']}**")
                st.info(f"💰 Total a pagar: **${reservation['total_amount']:.2f}**")
                
                # Opción de pagar ahora
                if st.button("💳 Pagar Ahora"):
                    process_payment(reservation['reservation_id'], reservation['total_amount'])
            else:
                st.error("❌ Error creando la reserva")

def show_my_reservations():
    """Mostrar reservas del usuario"""
    st.subheader("📋 Mis Reservas")
    
    headers = get_auth_headers()
    response = make_api_request("/reservations", "GET", headers=headers)
    
    if response.get("success"):
        reservations = response.get("data", [])
        
        if reservations:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                status_filter = st.selectbox("🔍 Filtrar por estado", 
                                           ["Todos", "pending", "confirmed", "paid", "cancelled"])
            
            with col2:
                sort_by = st.selectbox("📊 Ordenar por", 
                                     ["Fecha creación", "Check-in", "Estado"])
            
            # Aplicar filtros
            if status_filter != "Todos":
                reservations = [r for r in reservations if r["status"] == status_filter]
            
            # Mostrar reservas
            for reservation in reservations:
                status_color = {
                    "pending": "🟡",
                    "confirmed": "🔵", 
                    "paid": "🟢",
                    "cancelled": "🔴",
                    "checked_in": "🟣",
                    "checked_out": "⚫"
                }.get(reservation["status"], "⚪")
                
                with st.expander(f"{status_color} {reservation['confirmation_code']} - ${reservation['total_amount']:.2f}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**📋 Código:** {reservation['confirmation_code']}")
                        st.write(f"**🏨 Hotel:** {reservation.get('hotel_name', 'N/A')}")
                        st.write(f"**🛏️ Habitación:** {reservation.get('room_number', 'N/A')}")
                    
                    with col2:
                        st.write(f"**📅 Check-in:** {reservation['check_in_date']}")
                        st.write(f"**📅 Check-out:** {reservation['check_out_date']}")
                        st.write(f"**👥 Huéspedes:** {reservation['guests']}")
                    
                    with col3:
                        st.write(f"**📊 Estado:** {reservation['status'].title()}")
                        st.write(f"**💰 Total:** ${reservation['total_amount']:.2f}")
                        st.write(f"**📅 Creada:** {reservation['created_at'][:10]}")
                    
                    if reservation.get('special_requests'):
                        st.write(f"**📝 Solicitudes:** {reservation['special_requests']}")
                    
                    # Botones de acción
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if reservation['status'] in ['pending', 'confirmed'] and st.button(f"💳 Pagar", key=f"pay_{reservation['id']}"):
                            process_payment(reservation['id'], reservation['total_amount'])
                    
                    with col2:
                        if reservation['status'] not in ['cancelled', 'checked_out'] and st.button(f"❌ Cancelar", key=f"cancel_{reservation['id']}"):
                            cancel_reservation(reservation['id'])
                    
                    with col3:
                        if st.button(f"📄 Ver Detalles", key=f"details_{reservation['id']}"):
                            show_reservation_details(reservation['id'])
        else:
            st.info("ℹ️ No tienes reservas aún")
    else:
        st.error("❌ Error cargando reservas")

def process_payment(reservation_id: str, amount: float):
    """Procesar pago"""
    st.subheader("💳 Procesar Pago")
    
    with st.form("payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            payment_method = st.selectbox("💳 Método de Pago", 
                                        ["credit_card", "debit_card", "paypal", "stripe"])
            amount_display = st.number_input("💰 Monto", value=amount, disabled=True)
        
        with col2:
            currency = st.selectbox("💱 Moneda", ["USD", "EUR", "MXN"], index=0)
            
            if payment_method in ["credit_card", "debit_card"]:
                card_number = st.text_input("🔢 Número de Tarjeta", placeholder="1234 5678 9012 3456")
                cvv = st.text_input("🔒 CVV", placeholder="123", max_chars=3)
        
        pay_button = st.form_submit_button("💰 Procesar Pago", use_container_width=True)
        
        if pay_button:
            payment_data = {
                "reservation_id": reservation_id,
                "amount": amount,
                "currency": currency,
                "payment_method": payment_method,
                "payment_data": {}
            }
            
            if payment_method in ["credit_card", "debit_card"]:
                payment_data["payment_data"] = {
                    "card_number": card_number,
                    "cvv": cvv
                }
            
            headers = get_auth_headers()
            response = make_api_request("/payments", "POST", payment_data, headers)
            
            if response.get("success"):
                payment_result = response["data"]
                
                if payment_result["success"]:
                    st.success("✅ ¡Pago procesado exitosamente!")
                    st.info(f"📋 ID de transacción: {payment_result.get('transaction_id', 'N/A')}")
                else:
                    st.error("❌ Error procesando el pago")
            else:
                st.error("❌ Error en el servicio de pagos")

def show_payments():
    """Mostrar historial de pagos"""
    st.subheader("💳 Historial de Pagos")
    
    # Solo admin/hotel_manager pueden ver todos los pagos
    user_info = st.session_state.user_info
    if user_info['role'] in ['admin', 'hotel_manager']:
        headers = get_auth_headers()
        response = make_api_request("/payments", "GET", headers=headers)
        
        if response.get("success"):
            payments = response.get("data", [])
            
            if payments:
                # Crear DataFrame para mejor visualización
                df = pd.DataFrame(payments)
                
                # Métricas
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    total_amount = df['amount'].sum()
                    st.metric("💰 Total Procesado", f"${total_amount:.2f}")
                
                with col2:
                    completed_payments = df[df['status'] == 'completed'].shape[0]
                    st.metric("✅ Pagos Exitosos", completed_payments)
                
                with col3:
                    failed_payments = df[df['status'] == 'failed'].shape[0]
                    st.metric("❌ Pagos Fallidos", failed_payments)
                
                with col4:
                    avg_amount = df['amount'].mean()
                    st.metric("📊 Promedio", f"${avg_amount:.2f}")
                
                st.markdown("---")
                
                # Tabla de pagos
                st.dataframe(
                    df[['id', 'amount', 'currency', 'payment_method', 'status', 'processed_at']],
                    use_container_width=True
                )
                
                # Gráfico de pagos por método
                fig = px.pie(df, names='payment_method', title='Pagos por Método')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ No hay pagos registrados")
        else:
            st.error("❌ Error cargando pagos")
    else:
        st.warning("⚠️ Solo administradores pueden ver el historial completo de pagos")

def show_notifications():
    """Mostrar notificaciones"""
    st.subheader("🔔 Notificaciones")
    
    headers = get_auth_headers()
    response = make_api_request("/notifications", "GET", headers=headers)
    
    if response.get("success"):
        notifications = response.get("data", [])
        
        if notifications:
            # Filtros
            col1, col2 = st.columns(2)
            
            with col1:
                type_filter = st.selectbox("🔍 Tipo", ["Todos", "email", "sms", "push"])
            
            with col2:
                read_filter = st.selectbox("📖 Estado", ["Todos", "Leídas", "No leídas"])
            
            # Aplicar filtros
            filtered_notifications = notifications
            
            if type_filter != "Todos":
                filtered_notifications = [n for n in filtered_notifications if n["type"] == type_filter]
            
            if read_filter == "Leídas":
                filtered_notifications = [n for n in filtered_notifications if n["read"]]
            elif read_filter == "No leídas":
                filtered_notifications = [n for n in filtered_notifications if not n["read"]]
            
            # Mostrar notificaciones
            for notification in filtered_notifications:
                read_icon = "📖" if notification["read"] else "📬"
                type_icon = {"email": "📧", "sms": "📱", "push": "🔔"}.get(notification["type"], "🔔")
                
                with st.expander(f"{read_icon} {type_icon} {notification['subject']}"):
                    st.write(f"**📝 Mensaje:** {notification['message']}")
                    st.write(f"**📅 Fecha:** {notification['created_at'][:19]}")
                    st.write(f"**📊 Estado:** {'Enviada' if notification['sent'] else 'Pendiente'}")
                    
                    if not notification["read"]:
                        if st.button(f"✅ Marcar como leída", key=f"read_{notification['id']}"):
                            mark_notification_read(notification['id'])
        else:
            st.info("ℹ️ No tienes notificaciones")
    else:
        st.error("❌ Error cargando notificaciones")

def mark_notification_read(notification_id: str):
    """Marcar notificación como leída"""
    headers = get_auth_headers()
    response = make_api_request(f"/notifications/{notification_id}/read", "PATCH", headers=headers)
    
    if response.get("success"):
        st.success("✅ Notificación marcada como leída")
        st.rerun()
    else:
        st.error("❌ Error marcando notificación")

def cancel_reservation(reservation_id: str):
    """Cancelar reserva"""
    st.subheader("❌ Cancelar Reserva")
    
    reason = st.text_area("📝 Motivo de cancelación", placeholder="Opcional")
    
    if st.button("🗑️ Confirmar Cancelación"):
        headers = get_auth_headers()
        response = make_api_request(f"/reservations/{reservation_id}", "DELETE", 
                                   {"cancellation_reason": reason}, headers)
        
        if response.get("success"):
            st.success("✅ Reserva cancelada exitosamente")
            st.rerun()
        else:
            st.error("❌ Error cancelando reserva")

def show_hotel_management():
    """Gestión de hoteles (solo admin)"""
    st.subheader("🏨 Gestión de Hoteles")
    
    tab1, tab2 = st.tabs(["📋 Lista de Hoteles", "➕ Agregar Hotel"])
    
    with tab1:
        # Listar hoteles
        response = make_api_request("/hotels", "GET")
        
        if response.get("success"):
            hotels = response.get("data", [])
            
            if hotels:
                for hotel in hotels:
                    with st.expander(f"🏨 {hotel['name']} - {hotel['city']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**📍 Dirección:** {hotel['address']}")
                            st.write(f"**🏙️ Ciudad:** {hotel['city']}")
                            st.write(f"**🌍 País:** {hotel['country']}")
                            st.write(f"**🌟 Rating:** {hotel.get('rating', 'N/A')}/5")
                        
                        with col2:
                            st.write(f"**🛏️ Total Habitaciones:** {hotel['total_rooms']}")
                            if hotel.get('description'):
                                st.write(f"**📝 Descripción:** {hotel['description']}")
            else:
                st.info("ℹ️ No hay hoteles registrados")
        else:
            st.error("❌ Error cargando hoteles")
    
    with tab2:
        # Agregar nuevo hotel
        with st.form("hotel_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("🏨 Nombre del Hotel")
                address = st.text_input("📍 Dirección")
                city = st.text_input("🏙️ Ciudad")
                phone = st.text_input("📞 Teléfono")
            
            with col2:
                country = st.text_input("🌍 País")
                email = st.text_input("📧 Email")
                rating = st.number_input("🌟 Rating", min_value=0.0, max_value=5.0, step=0.1)
                description = st.text_area("📝 Descripción")
            
            submit_hotel = st.form_submit_button("🏨 Crear Hotel", use_container_width=True)
            
            if submit_hotel:
                if all([name, address, city, country]):
                    hotel_data = {
                        "name": name,
                        "description": description,
                        "address": address,
                        "city": city,
                        "country": country,
                        "phone": phone,
                        "email": email,
                        "rating": rating if rating > 0 else None,
                        "amenities": [],
                        "images": []
                    }
                    
                    headers = get_auth_headers()
                    response = make_api_request("/hotels", "POST", hotel_data, headers)
                    
                    if response.get("success"):
                        st.success("✅ Hotel creado exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ Error creando hotel")
                else:
                    st.warning("⚠️ Por favor completa los campos obligatorios")

def show_room_management():
    """Gestión de habitaciones (solo admin)"""
    st.subheader("🛏️ Gestión de Habitaciones")
    
    # Primero obtener lista de hoteles
    hotels_response = make_api_request("/hotels", "GET")
    
    if not hotels_response.get("success"):
        st.error("❌ Error cargando hoteles")
        return
    
    hotels = hotels_response.get("data", [])
    if not hotels:
        st.warning("⚠️ Primero debes crear al menos un hotel")
        return
    
    tab1, tab2 = st.tabs(["🛏️ Agregar Habitación", "📋 Lista de Habitaciones"])
    
    with tab1:
        with st.form("room_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                hotel_options = {hotel['id']: f"{hotel['name']} - {hotel['city']}" for hotel in hotels}
                selected_hotel = st.selectbox("🏨 Hotel", options=list(hotel_options.keys()), 
                                            format_func=lambda x: hotel_options[x])
                
                room_number = st.text_input("🔢 Número de Habitación")
                room_type = st.selectbox("🛏️ Tipo", ["single", "double", "twin", "triple", "suite", "presidential", "family"])
                capacity = st.number_input("👥 Capacidad", min_value=1, max_value=10, value=2)
            
            with col2:
                price_per_night = st.number_input("💰 Precio por Noche", min_value=0.0, value=100.0)
                description = st.text_area("📝 Descripción")
                is_available = st.checkbox("✅ Disponible", value=True)
            
            submit_room = st.form_submit_button("🛏️ Crear Habitación", use_container_width=True)
            
            if submit_room:
                if all([selected_hotel, room_number, room_type, capacity > 0, price_per_night > 0]):
                    room_data = {
                        "hotel_id": selected_hotel,
                        "room_number": room_number,
                        "room_type": room_type,
                        "description": description,
                        "capacity": capacity,
                        "price_per_night": price_per_night,
                        "amenities": [],
                        "images": [],
                        "is_available": is_available
                    }
                    
                    headers = get_auth_headers()
                    response = make_api_request("/rooms", "POST", room_data, headers)
                    
                    if response.get("success"):
                        st.success("✅ Habitación creada exitosamente!")
                        st.rerun()
                    else:
                        st.error("❌ Error creando habitación")
                else:
                    st.warning("⚠️ Por favor completa todos los campos obligatorios")
    
    with tab2:
        st.info("ℹ️ Para ver habitaciones específicas, usa la función de búsqueda")

def show_analytics():
    """Mostrar analytics y reportes (solo admin)"""
    st.subheader("📊 Analytics y Reportes")
    
    # Métricas generales
    col1, col2, col3, col4 = st.columns(4)
    
    # Simular datos (en producción vendrían de APIs)
    with col1:
        st.metric("🏨 Hoteles", "15", "↗️ +2")
    
    with col2:
        st.metric("🛏️ Habitaciones", "320", "↗️ +25")
    
    with col3:
        st.metric("📋 Reservas Mes", "1,248", "↗️ +18%")
    
    with col4:
        st.metric("💰 Ingresos Mes", "$45,670", "↗️ +12%")
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de reservas por día
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        reservations = [20 + i % 10 for i in range(len(dates))]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=reservations, mode='lines+markers', name='Reservas'))
        fig.update_layout(title='Reservas por Día - Enero 2024')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de ingresos por método de pago
        payment_methods = ['Tarjeta Crédito', 'PayPal', 'Transferencia', 'Efectivo']
        amounts = [35000, 8000, 2000, 670]
        
        fig = px.pie(values=amounts, names=payment_methods, title='Ingresos por Método de Pago')
        st.plotly_chart(fig, use_container_width=True)

def show_reservation_details(reservation_id: str):
    """Mostrar detalles completos de una reserva"""
    headers = get_auth_headers()
    response = make_api_request(f"/reservations/{reservation_id}", "GET", headers=headers)
    
    if response.get("success"):
        reservation = response["data"]
        
        st.subheader(f"📋 Detalles de Reserva: {reservation['confirmation_code']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**📋 Código:** {reservation['confirmation_code']}")
            st.write(f"**📊 Estado:** {reservation['status'].title()}")
            st.write(f"**👤 Usuario:** {reservation['user_id']}")
            st.write(f"**🏨 Hotel:** {reservation['hotel_id']}")
            st.write(f"**🛏️ Habitación:** {reservation['room_id']}")
        
        with col2:
            st.write(f"**📅 Check-in:** {reservation['check_in_date']}")
            st.write(f"**📅 Check-out:** {reservation['check_out_date']}")
            st.write(f"**👥 Huéspedes:** {reservation['guests']}")
            st.write(f"**💰 Total:** ${reservation['total_amount']:.2f}")
            st.write(f"**📅 Creada:** {reservation['created_at']}")
        
        if reservation.get('special_requests'):
            st.write(f"**📝 Solicitudes Especiales:** {reservation['special_requests']}")
        
        if reservation.get('cancelled_at'):
            st.write(f"**❌ Cancelada:** {reservation['cancelled_at']}")
            if reservation.get('cancellation_reason'):
                st.write(f"**📝 Motivo:** {reservation['cancellation_reason']}")
    else:
        st.error("❌ Error cargando detalles de la reserva")

# ==================== MAIN APP ====================

def main():
    """Función principal de la aplicación"""
    try:
        # Verificar conexión con la API
        response = make_api_request("/health")
        
        if not response.get("success"):
            st.error("🚨 Error de conexión con el servidor. Verifica que los servicios estén ejecutándose.")
            st.stop()
        
        # Mostrar página según estado de autenticación
        if is_authenticated():
            show_dashboard()
        else:
            show_login_page()
    
    except Exception as e:
        st.error(f"Error inesperado en la aplicación: {e}")
        st.info("Por favor recarga la página e intenta nuevamente.")

if __name__ == "__main__":
    main()
