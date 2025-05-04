import json
import os
import time
from datetime import date, timedelta # For calculating due dates

# --- Constants ---
USERS_FILE = "library_users.json"
BOOKS_FILE = "library_books.json"
BORROW_DURATION_DAYS = 14 # How many days a book can be borrowed

# --- ANSI Colors and Styles (from example) ---
class Style:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Utility Functions ---
def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def pause_and_continue():
    """Pauses execution until Enter is pressed"""
    input(f"\n{Style.YELLOW}Press Enter to continue...{Style.END}")

def print_header(title):
    """Prints a styled header"""
    clear_screen()
    print(f"\n{Style.BOLD}{Style.BLUE}📚 {title} 📚{Style.END}")
    print(f"{Style.YELLOW}{'=' * (len(title) + 6)}{Style.END}")

# --- Data Handling Functions ---
def load_data(filename):
    """Loads data from a JSON file."""
    if not os.path.exists(filename):
        return {} if filename == USERS_FILE else [] # Return empty dict for users, list for books
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"{Style.RED}Error reading {filename}. File might be corrupt.{Style.END}")
        return {} if filename == USERS_FILE else []
    except FileNotFoundError:
         return {} if filename == USERS_FILE else []

def save_data(filename, data):
    """Saves data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4) # indent=4 makes the JSON file readable
        return True
    except IOError as e:
        print(f"{Style.RED}Error saving data to {filename}: {e}{Style.END}")
        return False

def initialize_data():
    """Create default files if they don't exist"""
    # --- Users ---
    if not os.path.exists(USERS_FILE):
        print(f"Initializing {USERS_FILE}...")
        default_users = {
            "admin": {"password": "admin123", "role": "librarian"},
            "mridul": {"password": "jamesbond007", "role": "student"},
            "test": {"password": "test", "role": "student"}
        }
        save_data(USERS_FILE, default_users)

    # --- Books ---
    if not os.path.exists(BOOKS_FILE):
        print(f"Initializing {BOOKS_FILE}...")
        default_books = [
            {
                "id": 1,
                "title": "1984",
                "author": "George Orwell",
                "status": "Available",
                "borrower": None,
                "due_date": None,
                "summary": "A chilling portrait of a society under total surveillance and thought control."
            },
            {
                "id": 2,
                "title": "Leonardo Da Vinci",
                "author": "Walter Isacsson",
                "status": "Available",
                "borrower": None,
                "due_date": None,
                "summary": "An acclaimed biography exploring the life and mind of the ultimate Renaissance man, connecting his art and science."
            },
            {
                "id": 3,
                "title": "Sapiens: A Brief History of Humankind",
                "author": "Yuval Noah Harari",
                "status": "Checked Out",
                "borrower": "student1",
                "due_date": (date.today() - timedelta(days=5)).isoformat(), # Example: Due 5 days ago
                "summary": "An exploration of human history from the Stone Age to the present."
            },
            {
                "id": 4,
                "title": "Dune",
                "author": "Frank Herbert",
                "status": "Available",
                "borrower": None,
                "due_date": None,
                "summary": "Epic science fiction novel set on the desert planet Arrakis."
            }
        ]
        save_data(BOOKS_FILE, default_books)

# --- Core Logic Functions ---

def login():
    """User login interface"""
    print_header("University Library Login")
    users = load_data(USERS_FILE)
    if not users:
        print(f"{Style.RED}User data file not found or empty. Please run initialization.{Style.END}")
        exit()

    attempts = 3
    while attempts > 0:
        username = input(f" {Style.BOLD}Username:{Style.END} ").strip()
        # Use standard input for visible password typing
        password = input(f" {Style.BOLD}Password:{Style.END} ").strip()

        user_data = users.get(username) # Safely get user data

        if user_data and user_data["password"] == password:
            print(f"\n{Style.GREEN}✓ Login successful! Welcome, {username}.{Style.END}")
            time.sleep(1.5)
            return username, user_data["role"] # Return username and role
        else:
            attempts -= 1
            print(f"\n{Style.RED}✗ Invalid username or password. {attempts} attempts remaining.{Style.END}")
            time.sleep(1)
            if attempts == 0:
                print(f"{Style.RED}\n⚠ Too many failed attempts. Exiting.{Style.END}")
                exit()
            print("-" * 30) # Separator before next attempt

    return None, None # Should not be reached if attempts logic is correct

def display_book(book, detailed=False):
    """Formats and prints book information."""
    status_color = Style.GREEN if book["status"] == "Available" else Style.YELLOW
    print("-" * 60)
    print(f" {Style.BOLD}ID:{Style.END} {book['id']:<5} {Style.BOLD}Title:{Style.END} {Style.CYAN}{book['title']}{Style.END}")
    print(f" {'':<8}{Style.BOLD}Author:{Style.END} {book['author']}")
    print(f" {'':<8}{Style.BOLD}Status:{Style.END} {status_color}{book['status']}{Style.END}")
    if book["status"] == "Checked Out":
        print(f" {'':<8}{Style.BOLD}Borrower:{Style.END} {book.get('borrower', 'N/A')}")
        print(f" {'':<8}{Style.BOLD}Due Date:{Style.END} {Style.RED}{book.get('due_date', 'N/A')}{Style.END}")
    if detailed and book.get('summary'):
        print(f" {'':<8}{Style.BOLD}Summary:{Style.END} {book['summary']}")
    print("-" * 60)


def view_all_books():
    """Displays all books in the library."""
    print_header("Library Catalog")
    books = load_data(BOOKS_FILE)
    if not books:
        print(f"{Style.YELLOW}The library currently has no books.{Style.END}")
        return

    for book in books:
        display_book(book) # Show summary False by default
    print(f"\nTotal books: {len(books)}")


def search_books():
    """Searches books by title, author, or summary keyword."""
    print_header("Search Books")
    books = load_data(BOOKS_FILE)
    if not books:
        print(f"{Style.YELLOW}The library currently has no books to search.{Style.END}")
        return

    query = input(f" {Style.BOLD}Enter search term (title, author, keyword):{Style.END} ").lower().strip()
    if not query:
        print(f"{Style.RED}Search term cannot be empty.{Style.END}")
        return

    results = []
    for book in books:
        if (query in book["title"].lower() or
            query in book["author"].lower() or
            query in book.get("summary", "").lower()): # Use .get for summary safely
            results.append(book)

    if not results:
        print(f"\n{Style.RED}No books found matching '{query}'.{Style.END}")
    else:
        print(f"\n{Style.GREEN}Found {len(results)} matching books:{Style.END}")
        for book in results:
            display_book(book, detailed=True) # Show details in search results

def find_book_by_id(book_id):
    """Finds a specific book in the library list by its ID."""
    books = load_data(BOOKS_FILE)
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def checkout_book(username):
    """Allows a user to check out an available book."""
    print_header("Checkout Book")
    books = load_data(BOOKS_FILE)
    view_all_books() # Show available books first

    try:
        book_id_str = input(f"\n{Style.BOLD}Enter the ID of the book you want to check out:{Style.END} ").strip()
        if not book_id_str.isdigit():
             print(f"{Style.RED}Invalid ID format. Please enter a number.{Style.END}")
             return
        book_id = int(book_id_str)

        book_found = False
        for book in books:
            if book["id"] == book_id:
                book_found = True
                if book["status"] == "Available":
                    book["status"] = "Checked Out"
                    book["borrower"] = username
                    due = date.today() + timedelta(days=BORROW_DURATION_DAYS)
                    book["due_date"] = due.isoformat() # Store date as string YYYY-MM-DD

                    if save_data(BOOKS_FILE, books):
                        print(f"\n{Style.GREEN}✓ Book '{book['title']}' checked out successfully!{Style.END}")
                        print(f"{Style.YELLOW}  Due Date: {book['due_date']}{Style.END}")
                    else:
                         print(f"{Style.RED}Failed to save checkout information.{Style.END}")
                         # Optional: Revert changes in memory if save failed? (More complex)
                else:
                    print(f"\n{Style.RED}✗ Sorry, '{book['title']}' is currently checked out.{Style.END}")
                    print(f"  It is due on {book.get('due_date', 'N/A')}.")
                break # Exit loop once book is found and processed

        if not book_found:
            print(f"\n{Style.RED}✗ No book found with ID {book_id}.{Style.END}")

    except ValueError:
        print(f"{Style.RED}✗ Invalid input. Please enter a numeric book ID.{Style.END}")


def return_book(username, role):
    """Allows a user or librarian to return a checked-out book."""
    print_header("Return Book")
    books = load_data(BOOKS_FILE)

    # Show books currently checked out (potentially filtered by user if not librarian)
    borrowed_books = []
    print(f"{Style.BOLD}Books Currently Checked Out:{Style.END}")
    found_borrowed = False
    for book in books:
        if book["status"] == "Checked Out":
            # Librarian sees all, student sees only their own
            if role == 'librarian' or book.get("borrower") == username:
                 display_book(book)
                 borrowed_books.append(book)
                 found_borrowed = True

    if not found_borrowed:
         if role == 'librarian':
             print(f"\n{Style.YELLOW}No books are currently checked out from the library.{Style.END}")
         else:
             print(f"\n{Style.YELLOW}You ({username}) do not have any books currently checked out.{Style.END}")
         return

    try:
        book_id_str = input(f"\n{Style.BOLD}Enter the ID of the book you want to return:{Style.END} ").strip()
        if not book_id_str.isdigit():
             print(f"{Style.RED}Invalid ID format. Please enter a number.{Style.END}")
             return
        book_id = int(book_id_str)


        book_found = False
        for book in books:
             if book["id"] == book_id:
                book_found = True
                if book["status"] == "Checked Out":
                    # Double-check if the right person is returning (optional, librarians can override)
                     if role == 'librarian' or book.get("borrower") == username:
                        original_borrower = book.get("borrower", "N/A")
                        book["status"] = "Available"
                        book["borrower"] = None
                        book["due_date"] = None

                        if save_data(BOOKS_FILE, books):
                            print(f"\n{Style.GREEN}✓ Book '{book['title']}' returned successfully (was borrowed by {original_borrower}).{Style.END}")
                        else:
                             print(f"{Style.RED}Failed to save return information.{Style.END}")
                     else:
                         print(f"\n{Style.RED}✗ You cannot return this book as it was borrowed by {book.get('borrower', 'another user')}.{Style.END}")

                else:
                    print(f"\n{Style.RED}✗ Book '{book['title']}' is already marked as Available.{Style.END}")
                break # Exit loop once book processed

        if not book_found:
             print(f"\n{Style.RED}✗ No book found with ID {book_id} that is currently checked out { 'by you' if role != 'librarian' else '' } .{Style.END}")

    except ValueError:
        print(f"{Style.RED}✗ Invalid input. Please enter a numeric book ID.{Style.END}")


# --- Librarian Functions ---

def add_book():
    """Adds a new book to the library (Librarian only)."""
    print_header("Add New Book")
    books = load_data(BOOKS_FILE)

    try:
        # Generate next ID
        next_id = max(book["id"] for book in books) + 1 if books else 1

        title = input(f" {Style.BOLD}Title:{Style.END} ").strip()
        author = input(f" {Style.BOLD}Author:{Style.END} ").strip()
        summary = input(f" {Style.BOLD}Summary:{Style.END} ").strip()

        if not title or not author:
            print(f"\n{Style.RED}✗ Title and Author cannot be empty.{Style.END}")
            return

        # Basic duplicate check (by title and author)
        for book in books:
            if book['title'].lower() == title.lower() and book['author'].lower() == author.lower():
                 print(f"\n{Style.RED}✗ Error: A book with this title and author already exists (ID: {book['id']}).{Style.END}")
                 return

        new_book = {
            "id": next_id,
            "title": title,
            "author": author,
            "status": "Available",
            "borrower": None,
            "due_date": None,
            "summary": summary
        }

        books.append(new_book)

        if save_data(BOOKS_FILE, books):
             print(f"\n{Style.GREEN}✓ Book '{title}' by {author} (ID: {next_id}) added successfully!{Style.END}")
        else:
             print(f"{Style.RED}✗ Failed to save the new book.{Style.END}")

    except Exception as e:
        print(f"{Style.RED}An error occurred: {e}{Style.END}")

def view_users():
     """Displays all registered users (Librarian only)."""
     print_header("Manage Users - View All")
     users = load_data(USERS_FILE)
     if not users:
         print(f"{Style.YELLOW}No users found in the system.{Style.END}")
         return

     print(f"{Style.BOLD}{'Username':<20} {'Role':<15}{Style.END}")
     print("-" * 35)
     for username, data in users.items():
         print(f"{username:<20} {data.get('role', 'N/A'):<15}")
     print("-" * 35)


# --- Main Menu ---

def main_menu(username, role):
    """Displays the main menu and handles user choices."""
    while True:
        clear_screen()
        print(f"\n{Style.BOLD}{Style.HEADER}🏫 University Library - Main Menu{Style.END}")
        print(f"{Style.CYAN}Logged in as: {username} ({role.capitalize()}){Style.END}")
        print(f"{Style.YELLOW}{'=' * 40}{Style.END}")
        print(f" {Style.BOLD}1.{Style.END} Search Books")
        print(f" {Style.BOLD}2.{Style.END} View All Books")
        print(f" {Style.BOLD}3.{Style.END} Checkout Book")
        print(f" {Style.BOLD}4.{Style.END} Return Book")
        if role == "librarian":
            print(f" {Style.BOLD}{Style.UNDERLINE}Librarian Options:{Style.END}")
            print(f"   {Style.BOLD}5.{Style.END} Add New Book")
            print(f"   {Style.BOLD}6.{Style.END} View Users")
        print(f"\n {Style.BOLD}0.{Style.END} Logout & Exit")
        print(f"{Style.YELLOW}{'=' * 40}{Style.END}")

        choice = input(f"{Style.BOLD}Enter your choice:{Style.END} ").strip()

        if choice == '1':
            search_books()
            pause_and_continue()
        elif choice == '2':
            view_all_books()
            pause_and_continue()
        elif choice == '3':
            checkout_book(username)
            pause_and_continue()
        elif choice == '4':
            return_book(username, role)
            pause_and_continue()
        elif choice == '5' and role == 'librarian':
            add_book()
            pause_and_continue()
        elif choice == '6' and role == 'librarian':
            view_users()
            pause_and_continue()
        elif choice == '0':
            print(f"\n{Style.GREEN}Logging out. Goodbye, {username}!{Style.END}")
            time.sleep(1)
            clear_screen()
            break # Exit the while loop
        else:
            # Handle invalid choices or restricted access
            if role != 'librarian' and choice in ('5', '6'):
                print(f"\n{Style.RED}✗ Access Denied. Librarian role required.{Style.END}")
            else:
                print(f"\n{Style.RED}✗ Invalid choice. Please try again.{Style.END}")
            time.sleep(1.5)


# --- Main Execution ---
if __name__ == "__main__":
    initialize_data() # Ensure data files exist
    active_user, user_role = login()

    if active_user and user_role: # Only proceed if login was successful
        main_menu(active_user, user_role)