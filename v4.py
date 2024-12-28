import sys
import uuid
import json
import re
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkProxy

class Browser(QMainWindow):

    def __init__(self):
        super(Browser, self).__init__()

        # Set up the tabs for the browser
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)  # Enable closing tabs
        self.tabs.tabBarDoubleClicked.connect(self.open_new_tab)
        self.setCentralWidget(self.tabs)

        # Create the first tab
        self.create_new_tab(QUrl("https://duckduckgo.com"), "Home")  # Default to DuckDuckGo

        # Browser window settings
        self.showMaximized()
        self.setWindowTitle('IPsq')

        # Navigation bar
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)
        nav_bar.setStyleSheet("""
            background-color: #333;
            color: white;
            padding: 5px;
        """)  # Style the navigation bar

        # Back button
        back_btn = QAction('Back', self)
        back_btn.triggered.connect(self.navigate_back)
        nav_bar.addAction(back_btn)

        # Forward button
        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(self.navigate_forward)
        nav_bar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction('Reload', self)
        reload_btn.triggered.connect(self.reload_page)
        nav_bar.addAction(reload_btn)

        # Home button
        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        nav_bar.addAction(home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setStyleSheet("""
            border: 1px solid #555;
            border-radius: 5px;
            padding: 5px;
            color: white;
            background-color: #444;
            max-width: 400px;
        """)  # Style the URL bar
        nav_bar.addWidget(self.url_bar)

        # Bookmark button
        bookmark_btn = QAction('Bookmark', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        nav_bar.addAction(bookmark_btn)

        # Show MAC Address button
        mac_btn = QAction('Save MAC Address', self)
        mac_btn.triggered.connect(self.save_mac_address)
        nav_bar.addAction(mac_btn)

        # New Tab shortcut
        new_tab_action = QAction('New Tab', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.open_new_tab)
        self.addAction(new_tab_action)

        # Close Tab shortcut
        close_tab_action = QAction('Close Tab', self)
        close_tab_action.setShortcut('Ctrl+Z')
        close_tab_action.triggered.connect(self.close_current_tab)
        self.addAction(close_tab_action)

        # Download handling
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.currentWidget().page().profile().downloadRequested.connect(self.on_download_requested)

        # General window style
        self.setStyleSheet("""
            background-color: #222;
            color: white;
        """)  # Style the main window

    def create_new_tab(self, url, label):
        new_browser = QWebEngineView()
        new_browser.setUrl(url)
        new_browser.urlChanged.connect(self.update_url)

        # Add the browser view as the main content of the tab
        self.tabs.addTab(new_browser, label)
        self.tabs.setTabText(self.tabs.indexOf(new_browser), label)

        # Set the current tab
        self.tabs.setCurrentWidget(new_browser)

    def open_new_tab(self):
        self.create_new_tab(QUrl("https://duckduckgo.com"), "New Tab")  # Open DuckDuckGo in a new tab

    def close_tab(self, index):
        if self.tabs.count() > 1:  # Ensure there is at least one tab open
            self.tabs.removeTab(index)

    def close_current_tab(self):
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)

    def navigate_back(self):
        current_browser = self.tabs.currentWidget()
        current_browser.back()

    def navigate_forward(self):
        current_browser = self.tabs.currentWidget()
        current_browser.forward()

    def reload_page(self):
        current_browser = self.tabs.currentWidget()
        current_browser.reload()

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("https://duckduckgo.com"))  # Set home to DuckDuckGo

    def navigate_to_url(self):
        url = self.url_bar.text()
        if url.endswith('.onion'):
            self.route_via_tor(url)  # Route .onion domains via Tor
        else:
            # Check if it's a valid URL
            if url.startswith("http://") or url.startswith("https://"):
                self.tabs.currentWidget().setUrl(QUrl(url))
            else:
                search_url = f"https://duckduckgo.com/?q={url}"  # Redirect to DuckDuckGo for search
                self.tabs.currentWidget().setUrl(QUrl(search_url))

    def route_via_tor(self, url):
        proxy = QNetworkProxy()
        proxy.setType(QNetworkProxy.Socks5Proxy)
        proxy.setHostName("127.0.0.1")  # Tor listens on localhost
        proxy.setPort(9050)  # Default port for Tor SOCKS5 proxy
        QNetworkProxy.setApplicationProxy(proxy)

        self.tabs.currentWidget().setUrl(QUrl(url))  # Navigate to the .onion site

    def update_url(self, q):
        self.url_bar.setText(q.toString())

    def update_url_bar(self):
        current_browser = self.tabs.currentWidget()
        if current_browser:
            self.url_bar.setText(current_browser.url().toString())

    def add_bookmark(self):
        url = self.tabs.currentWidget().url().toString()
        with open('bookmarks.txt', 'a') as f:
            f.write(url + '\n')
        print(f'Bookmarked {url}')

    def save_mac_address(self):
        mac = self.get_mac_address()
        # Save MAC address to JSON file
        mac_data = {"mac_address": mac}
        with open('mac_address.json', 'w') as json_file:
            json.dump(mac_data, json_file)
        QMessageBox.information(self, "MAC Address", f"Your MAC Address has been saved to 'mac_address.json'.")

    def get_mac_address(self):
        # Automatically get the MAC address
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        return mac

    def on_download_requested(self, download_item):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", download_item.suggestedFileName())
        if path:
            download_item.setPath(path)
            download_item.accept()

# Main function to run the browser
app = QApplication(sys.argv)
QApplication.setApplicationName('IPsq')
window = Browser()
window.show()
app.exec_()
