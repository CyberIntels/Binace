@echo off
echo Создаем простую версию frontend...

cd frontend

echo Удаляем проблемные файлы...
if exist node_modules rmdir /s /q node_modules
if exist yarn.lock del yarn.lock
if exist package-lock.json del package-lock.json

echo Создаем простой package.json...
echo { > package_simple.json
echo   "name": "binance-trader-frontend", >> package_simple.json
echo   "version": "1.0.0", >> package_simple.json
echo   "private": true, >> package_simple.json
echo   "dependencies": { >> package_simple.json
echo     "react": "^18.2.0", >> package_simple.json
echo     "react-dom": "^18.2.0", >> package_simple.json
echo     "react-scripts": "5.0.1", >> package_simple.json
echo     "axios": "^1.6.0" >> package_simple.json
echo   }, >> package_simple.json
echo   "scripts": { >> package_simple.json
echo     "start": "react-scripts start", >> package_simple.json
echo     "build": "react-scripts build" >> package_simple.json
echo   }, >> package_simple.json
echo   "browserslist": { >> package_simple.json
echo     "production": [">0.2%", "not dead", "not op_mini all"], >> package_simple.json
echo     "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"] >> package_simple.json
echo   } >> package_simple.json
echo } >> package_simple.json

copy package_simple.json package.json
del package_simple.json

echo Устанавливаем простые зависимости...
npm install

cd ..

echo.
echo ✅ Готово! Теперь попробуйте:
echo    simple_start_npm.bat
echo.
pause