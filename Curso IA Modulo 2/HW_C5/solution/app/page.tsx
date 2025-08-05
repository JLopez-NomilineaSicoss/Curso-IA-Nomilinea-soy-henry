import { Button } from "@/components/ui/button"
import { ChevronDown, Monitor, FolderOpen, Users, Shield } from 'lucide-react'
import Image from "next/image"
import Link from "next/link"

export default function Component() {
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="border-b border-gray-100">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center">
              <div className="text-2xl font-bold text-gray-900">
                <span className="bg-yellow-400 text-black px-1">H</span>
                <span className="bg-yellow-400 text-black px-1">E</span>
                <span className="bg-yellow-400 text-black px-1">N</span>
                <span className="bg-yellow-400 text-black px-1">R</span>
                <span className="bg-yellow-400 text-black px-1">Y</span>
              </div>
            </div>

            {/* Navigation */}
            <nav className="hidden md:flex items-center space-x-8">
              <div className="flex items-center space-x-1 text-gray-700 hover:text-gray-900 cursor-pointer">
                <span>Para estudiantes</span>
                <ChevronDown className="h-4 w-4" />
              </div>
              <div className="flex items-center space-x-1 text-gray-700 hover:text-gray-900 cursor-pointer">
                <span>Para empresas</span>
                <ChevronDown className="h-4 w-4" />
              </div>
            </nav>

            {/* Auth buttons */}
            <div className="flex items-center space-x-4">
              <Link href="#" className="text-gray-700 hover:text-gray-900">
                Ingresar
              </Link>
              <Button className="bg-yellow-400 hover:bg-yellow-500 text-black font-medium px-6">
                Aplicar
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16 lg:py-24">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left Content */}
          <div className="space-y-8">
            <div className="space-y-6">
              <h1 className="text-4xl lg:text-5xl xl:text-6xl font-bold text-gray-900 leading-tight">
                Comienza o acelera tu carrera en tecnología
              </h1>
              <p className="text-xl text-gray-600">
                Estudia Desarrollo Full Stack, Data Science o Data Analytics.
              </p>
            </div>

            {/* Features */}
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded flex items-center justify-center">
                  <Monitor className="h-4 w-4 text-purple-600" />
                </div>
                <span className="text-gray-700">Online, en vivo y flexible</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded flex items-center justify-center">
                  <FolderOpen className="h-4 w-4 text-purple-600" />
                </div>
                <span className="text-gray-700">Basado en proyectos</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded flex items-center justify-center">
                  <Users className="h-4 w-4 text-purple-600" />
                </div>
                <span className="text-gray-700">Basado en cohortes</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-purple-100 rounded flex items-center justify-center">
                  <Shield className="h-4 w-4 text-purple-600" />
                </div>
                <span className="text-gray-700">Garantía de Empleo</span>
              </div>
            </div>

            {/* CTA Button */}
            <Button className="bg-yellow-400 hover:bg-yellow-500 text-black font-medium px-8 py-3 text-lg">
              Aplicar
            </Button>
          </div>

          {/* Right Image */}
          <div className="relative">
            <div className="relative rounded-2xl overflow-hidden">
              <Image
                src="/placeholder.svg?height=600&width=500"
                alt="Estudiante trabajando en computadora"
                width={500}
                height={600}
                className="w-full h-auto object-cover"
              />
            </div>
          </div>
        </div>

        {/* Bottom tagline */}
        <div className="text-center mt-16 lg:mt-24">
          <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">
            Bootcamp <span className="text-purple-600">#1</span> de Latam
          </h2>
        </div>
      </main>
    </div>
  )
}
