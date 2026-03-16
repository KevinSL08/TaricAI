# TARIC AI - Product Requirements Document

## Problem Statement
Crear una aplicación SaaS para consultar el TARIC (Arancel Integrado de las Comunidades Europeas). La aplicación permite buscar productos usando palabras clave y con inteligencia artificial obtener la nomenclatura arancelaria correcta, aranceles, tributos y documentos requeridos (fitosanitarios y no fitosanitarios) para importar productos.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI + MongoDB + emergentintegrations
- **AI**: OpenAI GPT-5.2 via Emergent LLM Key
- **Auth**: JWT-based authentication

## Design Theme (Updated Jan 2026)
- **Theme**: Futuristic Dark / Cyberpunk
- **Primary Background**: #0a0f1a (Deep dark blue)
- **Accent Color**: #00d4ff (Cyan/Turquoise)
- **Cards**: Cyber cards with glowing borders
- **Typography**: Plus Jakarta Sans (headings), IBM Plex Sans (body), JetBrains Mono (codes)
- **Reference**: taric-ai.vercel.app

## User Personas
1. **Importadores**: Empresas que importan productos a España/UE
2. **Agentes Aduaneros**: Profesionales de despacho aduanero
3. **Empresas de Logística**: Necesitan clasificar productos para sus clientes

## Core Requirements (Static)
- ✅ Búsqueda inteligente de productos con IA
- ✅ Códigos TARIC de 10 dígitos con desglose
- ✅ Cálculo de aranceles y tributos
- ✅ Lista de documentos requeridos (fitosanitarios/no fitosanitarios)
- ✅ Enlaces a fuentes oficiales (TARIC UE, Agencia Tributaria)
- ✅ Historial de búsquedas por usuario
- ✅ Autenticación JWT

## What's Been Implemented (Jan 2026)

### Backend
- User registration/login with JWT
- TARIC search endpoint with AI analysis (GPT-5.2)
- Search history management (CRUD)
- MongoDB integration

### Frontend (Futuristic Dark Theme)
- Landing page with cyberpunk hero section
- Live Classification Monitor display
- Feature cards with cyber styling
- Demo section with TARIC classifier
- User registration/login with dark theme forms
- Dashboard with cyber cards and glowing effects
- TARIC code display component (10-digit breakdown with segments)
- Duty calculator card with receipt style
- Document checklist component with badges
- Search history with delete functionality
- Tab navigation (Clasificar/Historial)

### Design Updates (Jan 2026)
- Complete redesign to match taric-ai.vercel.app
- Dark background (#0a0f1a) with cyan accents (#00d4ff)
- Cyber cards with glowing borders on hover
- Grid background pattern
- Status indicators with glow effects
- Example tags for quick search

## Known Issues
- None critical - AI search working correctly

## Prioritized Backlog

### P0 (Critical)
- N/A - Core functionality complete

### P1 (High Priority)
- Export results to PDF
- Bulk product search
- Price calculator with product value input

### P2 (Medium Priority)
- Multi-language support (English)
- Save favorite searches
- Compare multiple products side-by-side
- Email notifications for tariff changes

## Next Tasks
1. User adds balance to Universal Key to enable AI searches
2. Test AI search functionality end-to-end
3. Consider implementing PDF export for search results
