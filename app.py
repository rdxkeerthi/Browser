import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView

class Browser(QMainWindow):

    def __init__(self):
        super(Browser, self).__init__()

        # Set up the tabs for the browser
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.open_new_tab)
        self.setCentralWidget(self.tabs)

        # Create the first tab
        self.create_new_tab(QUrl("https://duckduckgo.com"), "Home")  # Default to DuckDuckGo

        # Browser window settings
        self.showMaximized()
        self.setWindowTitle('My Custom Browser')

        # Navigation bar
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)
        nav_bar.setStyleSheet("background-color: #333; color: white;")  # Style the navigation bar

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
        self.url_bar.setStyleSheet("border: 1px solid #555; border-radius: 5px; padding: 5px;")  # Style the URL bar
        nav_bar.addWidget(self.url_bar)

        # Bookmark button
        bookmark_btn = QAction('Bookmark', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        nav_bar.addAction(bookmark_btn)

        # Download handling
        self.tabs.currentChanged.connect(self.update_url_bar)
        self.tabs.currentWidget().page().profile().downloadRequested.connect(self.on_download_requested)

        # General window style
        self.setStyleSheet("background-color: #222; color: white;")  # Style the main window

    def create_new_tab(self, url, label):
        new_browser = QWebEngineView()
        new_browser.setUrl(url)
        new_browser.urlChanged.connect(self.update_url)
        self.tabs.addTab(new_browser, label)
        self.tabs.setCurrentWidget(new_browser)

    def open_new_tab(self, index):
        self.create_new_tab(QUrl("https://duckduckgo.com"), "New Tab")  # Open DuckDuckGo in a new tab

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
        # Check if it's a valid URL
        if url.startswith("http://") or url.startswith("https://"):
            self.tabs.currentWidget().setUrl(QUrl(url))
        else:
            search_url = f"https://duckduckgo.com/?q={url}"  # Redirect to DuckDuckGo for search
            self.tabs.currentWidget().setUrl(QUrl(search_url))

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

    def on_download_requested(self, download_item):
        path, _ = QFileDialog.getSaveFileName(self, "Save File", download_item.suggestedFileName())
        if path:
            download_item.setPath(path)
            download_item.accept()

# Main function to run the browser
app = QApplication(sys.argv)
QApplication.setApplicationName('My Custom Browser')
window = Browser()
window.show()
app.exec_()
