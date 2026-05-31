#!/bin/bash
echo "Compiling Mac Application..."
pyinstaller --noconfirm --onedir --windowed --name "Vibe-Code-This" --icon "images/AppIcon.icns" --add-data "workspace.json:." src/main.py

echo "Building DMG..."
dmgbuild -s dmg_settings.py -D app=dist/Vibe-Code-This.app "Vibe-Code-This" "dist/Vibe-Code-This.dmg"

echo "Organizing output into compiles_github/mac..."
mkdir -p compiles_github/mac
cp dist/Vibe-Code-This.dmg compiles_github/mac/

echo "Forcing DMG Icon metadata..."
python3 -c 'import Cocoa; Cocoa.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(Cocoa.NSImage.alloc().initWithContentsOfFile_("images/AppIcon.icns"), "compiles_github/mac/Vibe-Code-This.dmg", 0)'

echo "Done! Your DMG is inside compiles_github/mac/"
