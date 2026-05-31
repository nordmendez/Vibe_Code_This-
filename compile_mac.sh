#!/bin/bash
echo "Compiling Mac Application..."
pyinstaller --noconfirm --onedir --windowed --name "Vibe-Code-This" --icon "images/AppIcon.icns" --add-data "workspace.json:." src/main.py

echo "Building DMG..."
dmgbuild -s dmg_settings.py -D app=dist/Vibe-Code-This.app "Vibe-Code-This" "dist/Vibe-Code-This.dmg"

echo "Organizing output into compiles_github/mac..."
mkdir -p compiles_github/mac
cp dist/Vibe-Code-This.dmg compiles_github/mac/

echo "Done! Your DMG is inside compiles_github/mac/"
