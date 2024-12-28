# DuckDuckGo Privacy Browser with Ad Blocking and IP Masking

A customizable and privacy-centric browser built using PyQt5, featuring DuckDuckGo as the default search engine, an integrated ad blocker, and plans for IP masking functionality.

## Features

- **Private Searching**: DuckDuckGo ensures no search history or personal information is stored.
- **Ad Blocker**: Blocks intrusive ads from domains like Google Ads, Yahoo, and Facebook.
- **History and Bookmarks**: Save and manage your browsing history and bookmarks efficiently.
- **Lightweight Interface**: Developed with PyQt5 for a smooth and user-friendly experience.
- **Incognito Mode**: Optional incognito mode for enhanced privacy.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/rdxkeerthi/Browser.git
    cd Browser
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python v5.py
    ```

## Usage

1. Launch the browser by running `python v5.py`.
2. Use the navigation bar to browse with DuckDuckGo.
3. Manage bookmarks, history, and enjoy ad-free browsing.

## Requirements

- Python 3.8 or later
- PyQt5

## Architecture

- **Ad Blocking**: Blocks requests to predefined domains in `AdBlocker` class.
- **Bookmark and History Management**: JSON-based storage for easy export and import.
- **Navigation Bar**: Provides buttons for navigation, bookmarking, and accessing history.
- **User Interface**: Developed with PyQt5 for a cross-platform graphical interface.

## Future Enhancements

- **IP Masking**: Implement proxy routing for Tor-like anonymity.
- **Improved Ad Blocking**: Allow user-defined blocking rules.
- **Custom Themes**: Enable users to customize the browser’s appearance.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Disclaimer

This browser is intended for personal use and privacy-focused browsing. It is not a replacement for specialized anonymity tools like Tor.


