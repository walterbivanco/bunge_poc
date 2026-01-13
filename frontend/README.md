# Bunge Bot Assistant

Un asistente de chat interactivo construido con React y TypeScript. Esta es una aplicación de demostración que muestra una interfaz de usuario profesional para un chatbot conversacional.

## 📋 Características

- **Interfaz de chat moderna**: Diseño limpio y responsivo con soporte para múltiples conversaciones
- **Historial de conversaciones**: Guarda y gestiona múltiples conversaciones en el sidebar
- **Diseño responsive**: Interfaz que se adapta a diferentes tamaños de pantalla
- **Componentes reutilizables**: Utiliza shadcn-ui para componentes de UI de alta calidad
- **Tema profesional**: Basado en Tailwind CSS con un diseño personalizado de Bunge

## 🛠️ Tecnologías

Este proyecto está construido con:

- **Vite** - Herramienta de construcción y servidor de desarrollo de alta velocidad
- **React** - Librería de UI
- **TypeScript** - Tipado estático para JavaScript
- **Tailwind CSS** - Framework de CSS utilitario
- **shadcn-ui** - Componentes de UI de alta calidad
- **React Router** - Enrutamiento de la aplicación
- **TanStack Query** - Gestión de estado y cache de datos

## 🚀 Cómo levantar el proyecto

### Requisitos previos

- **Node.js** (versión 18 o superior) - [Instalar Node.js](https://nodejs.org/)
- **npm** o **bun** como gestor de paquetes

### Instalación y ejecución

```sh
# Paso 1: Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>

# Paso 2: Navegar al directorio del proyecto
cd bunge-bot-assistant

# Paso 3: Instalar las dependencias
npm install
# o si usas bun:
# bun install

# Paso 4: Iniciar el servidor de desarrollo
npm run dev
# o si usas bun:
# bun run dev
```

La aplicación estará disponible en `http://localhost:8080`

### Comandos disponibles

```sh
# Desarrollo con recarga en caliente
npm run dev

# Construir para producción
npm run build

# Construir en modo desarrollo
npm run build:dev

# Vista previa de la compilación
npm run preview

# Ejecutar linter (ESLint)
npm run lint
```

## ⚠️ Datos Mock - Cambios necesarios

La aplicación actualmente utiliza **datos mock (simulados)** en varios lugares. Estos deben ser reemplazados cuando se integre con una API real:

### 1. **Respuestas del Asistente** (`src/pages/Index.tsx`)

Las respuestas del chatbot son simuladas con un conjunto predefinido de textos:

```typescript
const responses = [
  "¡Gracias por tu mensaje! Estoy aquí para ayudarte con cualquier consulta.",
  "Entiendo tu pregunta. Déjame proporcionarte la mejor información posible.",
  "¡Excelente pregunta! Te cuento más detalles sobre eso.",
  "Claro, con gusto te ayudo. ¿Hay algo específico que necesites saber?",
];
```

**Cambio necesario**: Reemplazar con llamadas a una API real que procese las preguntas del usuario y devuelva respuestas inteligentes.

### 2. **Simulación de escritura** (`src/pages/Index.tsx`)

La respuesta del asistente simula un delay aleatorio:

```typescript
await new Promise((resolve) => setTimeout(resolve, 1200 + Math.random() * 800));
```

**Cambio necesario**: Reemplazar con el tiempo real de respuesta de la API.

### 3. **Gestión de conversaciones** (`src/pages/Index.tsx`)

Las conversaciones se almacenan solo en estado local (no persisten al recargar):

```typescript
const [conversations, setConversations] = useState<Conversation[]>([]);
const [messages, setMessages] = useState<Message[]>([]);
```

**Cambio necesario**: Integrar con una base de datos para persistencia de datos.

### 4. **Logo de Bunge** (`src/components/chat/ChatSidebar.tsx`)

El logo se importa de assets locales:

```typescript
import logoBunge from "@/assets/logo-bunge.svg";
```

Asegúrate de que el archivo del logo esté presente en `src/assets/logo-bunge.svg`.

## 📁 Estructura del proyecto

```
src/
├── components/
│   ├── chat/              # Componentes relacionados al chat
│   │   ├── ChatArea.tsx
│   │   ├── ChatInputArea.tsx
│   │   ├── ChatMessage.tsx
│   │   ├── ChatSidebar.tsx
│   │   └── WelcomeScreen.tsx
│   └── ui/                # Componentes de UI reutilizables (shadcn-ui)
├── hooks/                 # Custom React hooks
├── lib/                   # Funciones utilitarias
├── pages/                 # Páginas principales
│   ├── Index.tsx          # Página principal con lógica del chat
│   └── NotFound.tsx       # Página 404
├── App.tsx                # Componente raíz
└── main.tsx               # Punto de entrada
```

## 🔧 Configuración

### Vite Config (`vite.config.ts`)

El servidor de desarrollo está configurado para escuchar en `localhost:8080`. Esto puede modificarse en caso de necesario.

### TypeScript

El proyecto utiliza TypeScript strict. Consulta `tsconfig.json` para la configuración completa.

### Tailwind CSS

La configuración de Tailwind se encuentra en `tailwind.config.ts` con variables de tema personalizadas para Bunge.

## 📝 Próximos pasos

1. **Conectar API real**: Reemplazar las respuestas mock con llamadas a una API de backend
2. **Base de datos**: Implementar persistencia de conversaciones y mensajes
3. **Autenticación**: Agregar sistema de usuarios si es necesario
4. **Despliegue**: Configurar CI/CD y desplegar a producción

## 📄 Licencia

Este proyecto es propiedad de Taligent.
