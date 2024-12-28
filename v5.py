import sys
import json
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtGui import QPalette, QColor, QIcon

class AdBlocker:
    def __init__(self):
        self.blocked_domains = set([
            "doubleclick.net", "adservice.google.com", "googlesyndication.com",
            "ads.yahoo.com", "adnxs.com", "adsfacebook.com"
        ])

    def intercept_request(self, url):
        for domain in self.blocked_domains:
            if domain in url:
                print(f'Blocked ad: {url}')
                return True  # Indicates the request should be blocked
        return False  # Indicates the request can proceed

class Browser(QMainWindow):
    def __init__(self, incognito=False):
        super(Browser, self).__init__()
        self.incognito = incognito
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(self.open_new_tab)
        self.setCentralWidget(self.tabs)

        self.history = self.load_history()
        self.bookmarks = self.load_bookmarks()

        self.create_new_tab(QUrl("https://duckduckgo.com"), "Home")
        self.showMaximized()
        self.setWindowTitle('Custom Browser')

        self.create_navigation_bar()
        self.create_shortcuts()
        self.setup_styles()

        # Set up ad blocker
        self.ad_blocker = AdBlocker()
        profile = QWebEngineProfile.defaultProfile()
        profile.setRequestInterceptor(self)

    def load_bookmarks(self):
        try:
            with open('bookmarks.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_bookmarks(self):
        with open('bookmarks.json', 'w') as f:
            json.dump(self.bookmarks, f, indent=4)

    def load_history(self):
        try:
            with open('history.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_history(self):
        with open('history.json', 'w') as f:
            json.dump(self.history, f, indent=4)

    def open_new_tab(self):
        self.create_new_tab(QUrl("https://duckduckgo.com"), "New Tab")

    def close_tab(self, index):
        if self.tabs.count() > 1:
            current_browser = self.tabs.widget(index)
            if self.tabs.currentIndex() == index:
                if index > 0:
                    self.tabs.setCurrentIndex(index - 1)
                else:
                    self.tabs.setCurrentIndex(0)
            self.tabs.removeTab(index)
            current_browser.deleteLater()

    def create_navigation_bar(self):
        nav_bar = QToolBar()
        self.addToolBar(nav_bar)

        back_btn = QAction(QIcon('icons/back.png'), 'Back', self)
        back_btn.triggered.connect(self.navigate_back)
        nav_bar.addAction(back_btn)

        forward_btn = QAction(QIcon('icons/forward.png'), 'Forward', self)
        forward_btn.triggered.connect(self.navigate_forward)
        nav_bar.addAction(forward_btn)

        reload_btn = QAction(QIcon('icons/reload.png'), 'Reload', self)
        reload_btn.triggered.connect(self.reload_page)
        nav_bar.addAction(reload_btn)

        home_btn = QAction(QIcon('icons/home.png'), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        nav_bar.addAction(home_btn)

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        nav_bar.addWidget(self.url_bar)

        bookmark_btn = QAction(QIcon('icons/bookmark.png'), 'Bookmark', self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        nav_bar.addAction(bookmark_btn)

        bookmarks_btn = QAction(QIcon('icons/bookmarks.png'), 'Bookmarks', self)
        bookmarks_btn.triggered.connect(self.view_bookmarks)
        nav_bar.addAction(bookmarks_btn)

        history_btn = QAction(QIcon('icons/history.png'), 'History', self)
        history_btn.triggered.connect(self.view_history)
        nav_bar.addAction(history_btn)

    def add_bookmark(self):
        current_url = self.tabs.currentWidget().url().toString()
        title, ok = QInputDialog.getText(self, "Bookmark Title", "Enter a title for the bookmark:", text=current_url)
        if ok and title:
            if {"title": title, "url": current_url} not in self.bookmarks:
                self.bookmarks.append({"title": title, "url": current_url})
                self.save_bookmarks()
                QMessageBox.information(self, "Bookmark Added", f"Bookmarked {title}")
            else:
                QMessageBox.warning(self, "Already Bookmarked", "This page is already bookmarked.")

    def view_bookmarks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Bookmarks")
        dialog.setModal(True)
        dialog.resize(400, 300)
        layout = QVBoxLayout()

        list_widget = QListWidget()
        for bm in self.bookmarks:
            item = QListWidgetItem(f"{bm['title']} - {bm['url']}")
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self.edit_bookmark(list_widget))
        layout.addWidget(edit_btn)

        add_btn = QPushButton("Add New Bookmark")
        add_btn.clicked.connect(self.add_new_bookmark)
        layout.addWidget(add_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def edit_bookmark(self, list_widget):
        selected_item = list_widget.currentItem()
        if selected_item:
            title, url = self.extract_title_url(selected_item.text())
            self.show_bookmark_dialog(title, url, "Edit Bookmark", lambda t, u: self.update_bookmark(selected_item, t, u))

    def add_new_bookmark(self):
        self.show_bookmark_dialog("", "", "Add Bookmark", self.add_bookmark_from_dialog)

    def show_bookmark_dialog(self, title, url, dialog_title, callback):
        dialog = QDialog(self)
        dialog.setWindowTitle(dialog_title)
        layout = QVBoxLayout()

        title_input = QLineEdit(title)
        url_input = QLineEdit(url)
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_input)
        layout.addWidget(QLabel("URL:"))
        layout.addWidget(url_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: callback(title_input.text(), url_input.text()))
        layout.addWidget(save_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def update_bookmark(self, list_widget_item, new_title, new_url):
        index = self.bookmarks.index(next(bm for bm in self.bookmarks if bm["title"] == list_widget_item.text().split(" - ")[0]))
        self.bookmarks[index] = {"title": new_title, "url": new_url}
        self.save_bookmarks()
        list_widget_item.setText(f"{new_title} - {new_url}")
        QMessageBox.information(self, "Bookmark Updated", "Bookmark updated successfully.")

    def add_bookmark_from_dialog(self, title, url):
        if {"title": title, "url": url} not in self.bookmarks and title and url:
            self.bookmarks.append({"title": title, "url": url})
            self.save_bookmarks()
            QMessageBox.information(self, "Bookmark Added", f"Bookmarked {title}")
        else:
            QMessageBox.information(self, "Already Bookmarked", "This page is already bookmarked or invalid.")

    def extract_title_url(self, bookmark_str):
        title, url = bookmark_str.split(' - ')
        return title, url

    def view_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("History")
        dialog.setModal(True)
        dialog.resize(400, 300)
        layout = QVBoxLayout()

        list_widget = QListWidget()
        for url in self.history[::-1]:
            item = QListWidgetItem(url)
            list_widget.addItem(item)

        layout.addWidget(list_widget)

        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_btn)

        open_btn = QPushButton("Open")
        open_btn.clicked.connect(lambda: self.open_history_page(list_widget))
        layout.addWidget(open_btn)

        dialog.setLayout(layout)
        dialog.exec_()

    def clear_history(self):
        self.history.clear()
        self.save_history()
        QMessageBox.information(self, "History Cleared", "Browser history has been cleared.")
class Browser(QMainWindow):
    def __init__(self, incognito=False):
        super(Browser, self).__init__()
        self.incognito = incognito
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(self.open_new_tab)
        self.setCentralWidget(self.tabs)

        self.history = self.load_history()
        self.bookmarks = self.load_bookmarks()

        # Create the home tab
        self.create_new_tab(QUrl("https://duckduckgo.com"), "Home")
        self.showMaximized()
        self.setWindowTitle('Custom Browser')

        self.create_navigation_bar()
        self.create_shortcuts()
        self.setup_styles()

        # Set up ad blocker
        self.ad_blocker = AdBlocker()
        profile = QWebEngineProfile.defaultProfile()
        profile.setRequestInterceptor(self)

    def create_new_tab(self, url, title):
        """Create a new tab with the given URL and title."""
        browser_view = QWebEngineView()
        browser_view.setUrl(url)

        # Connect signals to handle URL changes and history
        browser_view.urlChanged.connect(self.update_url_bar)
        browser_view.loadFinished.connect(lambda _, title=title: self.tabs.setTabText(self.tabs.indexOf(browser_view), title))

        # Add the new tab to the tab widget
        self.tabs.addTab(browser_view, title)
        self.tabs.setCurrentWidget(browser_view)

        # Add the URL to history
        self.history.append(url.toString())
        self.save_history()

    # ... rest of your methods here ...

# Add the rest of your browser methods here...

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Custom Browser")
    window = Browser()
    app.exec_()
