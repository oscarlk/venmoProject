- using Conda env to run backend
- client secret and gmail token are included in gitignore

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

- to run frontend: npm run dev

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.

Working Demo:
![image](https://github.com/user-attachments/assets/dcabb015-9a03-488b-b1a3-dc7e38fc9969)

Steps to run:

1. Backend
   - go to backend directory
   - pip install requirements.txt
   - make sure to have .env file
   - python server.py
  
2. Frontend
   - go to frontend directory
   - npm install
   - npm run dev
