@echo off
echo Исправляем совместимость с Node.js v14...

cd frontend

echo Удаляем node_modules...
if exist node_modules rmdir /s /q node_modules

echo Удаляем yarn.lock...
if exist yarn.lock del yarn.lock

echo Устанавливаем совместимые версии пакетов...
yarn add react@^17.0.2 react-dom@^17.0.2 react-scripts@4.0.3
yarn add @craco/craco@6.4.5

echo Переустанавливаем все зависимости...
yarn install --network-concurrency 1

cd ..

echo.
echo ✅ Готово! Теперь попробуйте:
echo    simple_start.bat
echo.
pause