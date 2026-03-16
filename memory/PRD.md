# TARIC AI - Product Requirements Document

## Problem Statement
Crear una aplicación SaaS B2B para agencias de aduanas que permita consultar el TARIC (Arancel Integrado de las Comunidades Europeas). La aplicación permite buscar productos usando palabras clave y con inteligencia artificial obtener la nomenclatura arancelaria correcta, aranceles, tributos y documentos requeridos (fitosanitarios y no fitosanitarios). Gestión de equipos empresariales y datos 100% de fuentes oficiales.

## Architecture
- **Frontend**: React 19 + Tailwind CSS + Shadcn/UI + Framer Motion
- **Backend**: FastAPI + MongoDB + emergentintegrations
- **AI**: OpenAI GPT-5.2 via Emergent LLM Key
- **Auth**: JWT-based authentication with organizations

## Design Theme (Updated Jan 2026)
- **Theme**: Futuristic Dark / Cyberpunk
- **Primary Background**: #0a0f1a (Deep dark blue)
- **Accent Color**: #00d4ff (Cyan/Turquoise)
- **Cards**: Cyber cards with glowing borders
- **Animations**: Framer Motion for smooth transitions
- **Typography**: Plus Jakarta Sans (headings), IBM Plex Sans (body), JetBrains Mono (codes)

## User Personas
1. **Agencias de Aduanas**: Empresas que gestionan despacho aduanero
2. **Importadores B2B**: Empresas que importan productos a España/UE
3. **Operadores de Comercio Exterior**: Profesionales de logística internacional

## Core Requirements (Static)
- ✅ Búsqueda inteligente de productos con IA (GPT-5.2)
- ✅ Códigos TARIC de 10 dígitos con desglose visual
- ✅ Cálculo de aranceles con preferencias arancelarias
- ✅ Alertas de compliance (anti-dumping, sanciones, CITES)
- ✅ Lista de documentos (fitosanitarios/no fitosanitarios) con autoridades
- ✅ Enlaces a fuentes oficiales verificadas (UE + España)
- ✅ Gestión de equipos B2B (Admin, Operador, Consultor)
- ✅ Referencia de cliente para trazabilidad
- ✅ Historial de búsquedas con atribución de usuario
- ✅ Estadísticas de organización

## What's Been Implemented (Jan 2026)

### Backend v2.0.0
- User registration with automatic organization creation
- JWT authentication with organization context
- Team management endpoints (invite, remove, list)
- Organization statistics (searches, members, operations)
- TARIC search with AI and compliance alerts
- Regulatory alerts endpoint (anti-dumping, restrictions)
- Search history with user attribution

### Frontend (B2B Professional)
- Landing page B2B enfocada:
  - Hero con "Plataforma B2B para Agencias de Aduanas"
  - Sección "Problemas que Resolvemos" con falencias del sector
  - Sección "Fuentes Oficiales 100%" con logos
  - Sección de precios B2B (Starter, Professional, Enterprise)
  - Compromiso de fiabilidad
- Dashboard empresarial:
  - Tarjetas de estadísticas (clasificaciones, equipo, compliance)
  - Tabs: Clasificar, Historial, Equipo (admin)
  - Campo de referencia cliente para B2B
  - Alertas de compliance en resultados
- Gestión de equipos:
  - Invitar miembros con roles
  - Eliminar miembros
  - Ver estado de miembros

### Official Sources Integration
- TARIC - Comisión Europea (DG TAXUD)
- Agencia Tributaria (AEAT)
- Ministerio de Agricultura (MAPA)
- EUR-Lex (DOUE)

## Known Issues
- None critical

## Prioritized Backlog

### P0 (Critical) - DONE
- ✅ Core TARIC classification with AI
- ✅ B2B team management
- ✅ Compliance alerts

### P1 (High Priority)
- Export results to PDF
- Bulk product classification
- Email notifications for team invites
- Password recovery flow

### P2 (Medium Priority)
- Multi-language support (English)
- Save favorite searches
- Custom tariff calculators
- API access for Enterprise
- Audit log for compliance

## Next Tasks
1. Implement PDF export for search results
2. Add email service for team invitations
3. Build admin panel for super users
4. Add audit trail for compliance requirements
