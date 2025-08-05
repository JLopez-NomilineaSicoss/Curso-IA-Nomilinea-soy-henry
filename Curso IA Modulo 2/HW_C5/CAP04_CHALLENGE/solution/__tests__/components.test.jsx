import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { Component } from '../components/component';

describe('Component', () => {
  test('renders navbar', () => {
    render(<Component />)
    const navbar = screen.getByRole('navigation');
    expect(navbar).toBeInTheDocument();
  });

  test('renders logo', () => {
    render(<Component />);
    const logo = screen.getByAltText('Henry Logo');
    expect(logo).toBeInTheDocument();
  });

  test('renders hero section', () => {
    render(<Component />);
    const heading = screen.getByRole('heading', {
      name: /Comienza o acelera tu carrera en tecnología/i,
    });
    expect(heading).toBeInTheDocument();
  });

  test('renders feature list', () => {
    render(<Component />);
    const features = screen.getAllByRole('listitem');
    expect(features).toHaveLength(4);
  });

  // New test for "Aplicar" button
  test('renders "Aplicar" button', () => {
    render(<Component />);
    const aplicarElements = screen.getAllByText(/Aplicar/i);
    expect(aplicarElements.length).toBeGreaterThan(1);
  });

    // New test for "Ingresar" link
    test('renders "Para estudiantes" link', () => {
      render(<Component />);
      // This will find any element with "Ingresar" text, including links
      const ingresarLink = screen.getByText(/Para estudiantes/i);
      expect(ingresarLink).toBeInTheDocument();
    });
  
      // New test for "Ingresar" link
    test('renders "Para empresas" link', () => {
      render(<Component />);
      // This will find any element with "Ingresar" text, including links
      const ingresarLink = screen.getByText(/Para empresas/i);
      expect(ingresarLink).toBeInTheDocument();
    });

      // New test for "Ingresar" link
      test('renders "Basado en cohortes" link', () => {
        render(<Component />);
        // This will find any element with "Ingresar" text, including links
        const ingresarLink = screen.getByText(/Para empresas/i);
        expect(ingresarLink).toBeInTheDocument();
      });

  // New test for "Ingresar" link
  test('renders "Ingresar" link', () => {
    render(<Component />);
    // This will find any element with "Ingresar" text, including links
    const ingresarLink = screen.getByText(/Ingresar/i);
    expect(ingresarLink).toBeInTheDocument();
  });

  // Additional tests for design elements
  test('renders hero description text', () => {
    render(<Component />);
    const description = screen.getByText(/Estudia Desarrollo Full Stack, Data Science o Data Analytics/i);
    expect(description).toBeInTheDocument();
  });

  test('renders all feature items correctly', () => {
    render(<Component />);
    const onlineFeature = screen.getByText(/Online, en vivo y flexible/i);
    const proyectosFeature = screen.getByText(/Basado en proyectos/i);
    const cohortesFeature = screen.getByText(/Basado en cohortes/i);
    const empleoFeature = screen.getByText(/Garantía de Empleo/i);
    
    expect(onlineFeature).toBeInTheDocument();
    expect(proyectosFeature).toBeInTheDocument();
    expect(cohortesFeature).toBeInTheDocument();
    expect(empleoFeature).toBeInTheDocument();
  });

  test('renders footer banner', () => {
    render(<Component />);
    const footerBanner = screen.getByText(/Bootcamp #1 de Latam/i);
    expect(footerBanner).toBeInTheDocument();
  });

  test('renders hero image', () => {
    render(<Component />);
    const heroImage = screen.getByAltText(/Estudiantes en el bootcamp/i);
    expect(heroImage).toBeInTheDocument();
  });
});
