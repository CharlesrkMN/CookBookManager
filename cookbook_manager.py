import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection"""
    conn = None
    try:
        conn = sqlite3.connect('hipster_cookbooks.db')
        print(f"Successfully connected to SQLite {sqlite3.version} ")
        return conn
    except Error as e:
        print(f"Error establishing connection with the void: {e}")
        return None

def create_table(conn):
    """Create a table structure"""
    try:
        #sql statement to create cookbooks table
        sql_create_cookbooks_table = """
        CREATE TABLE IF NOT EXISTS cookbooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            year_published INTEGER,
            aesthetic_rating INTEGER,
            instagram_worthy BOOLEAN,
            cover_color TEXT
        );"""
        
        #sql statement to create cookbook tags table
        sql_create_tags_table = """
        CREATE TABLE IF NOT EXISTS tags_table (
            tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag TEXT NOT NULL,
            cookbook_id INTEGER,
            FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id)
        );"""

        #sql statement to create borrowed cookbooks table
        sql_create_borrow_table = """
        CREATE TABLE IF NOT EXISTS borrow_table (
            borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            friend_name TEXT NOT NULL,
            date_borrowed TEXT NOT NULL,
            date_returned TEXT,
            cookbook_id INTEGER,
            FOREIGN KEY (cookbook_id) REFERENCES cookbooks(id)
        );"""
    
        
        cursor = conn.cursor()
        cookbooks_notEmpty = cursor.execute('SELECT * FROM cookbooks') #check  to see if cookbooks table isnt empty
        tags_notEmpty = cursor.execute('SELECT * FROM tags_table') #check to see if tags table isnt empty
        borrow_notEmpty = cursor.execute('SELECT * FROM borrow_table') #check to see if borrow table isnt empty

    #if any tables dont start as empty, delete all records in them
        if cookbooks_notEmpty:
            cursor.execute("DELETE FROM cookbooks")
        if tags_notEmpty:
            cursor.execute("DELETE FROM tags_table")
        if borrow_notEmpty:
            cursor.execute("DELETE FROM borrow_table")
        
    #execute to create all tables
        cursor.execute(sql_create_cookbooks_table)
        cursor.execute(sql_create_tags_table)
        cursor.execute(sql_create_borrow_table)
        print("Successfully created a database structure")
    except Error as e:
        print(f"Error creating table: {e}")

def insert_cookbook(conn, cookbook):
    """Add a new cookbook to your shelf )"""
    sql = '''INSERT INTO cookbooks(title, author, year_published, aesthetic_rating, instagram_worthy, cover_color)
             VALUES(?,?,?,?,?,?)'''
    try:
        cursor = conn.cursor()
        cursor.execute(sql, cookbook)
        conn.commit()
        print(f"Successfully curated cookbook with id: {cursor.lastrowid}")
        return cursor.lastrowid
    except Error as e:
        print(f"Error adding to collection: {e}")
        return None

def get_all_cookbooks(conn):
    """Browse your entire collection """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cookbooks")
        books = cursor.fetchall()
        for book in books:
            print(f"ID: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"Author: {book[2]}")
            print(f"Published: {book[3]} (vintage is better)")
            print(f"Aesthetic Rating: {'✨' * book[4]}")
            print(f"Instagram Worthy: {'📸 Yes' if book[5] else 'Not aesthetic enough'}")
            print(f"Cover Color: {book[6]}")
            print("---")
        return books
    except Error as e:
        print(f"Error retrieving collection: {e}")
        return []
    
def search_by_aesthetic_rating(conn, minimum_rating):
    try:
        print("\nThese books match your rating: ")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cookbooks WHERE aesthetic_rating == ? ORDER BY cover_color", (minimum_rating)) #select all cookbook entries where the aesthetic rating = user input
        matches = cursor.fetchall()
        for match in matches: #display all matches to user input
            print(f"ID: {match[0]}")
            print(f"Title: {match[1]}")
            print(f"Author: {match[2]}")
            print(f"Published: {match[3]} (vintage is better)")
            print(f"Aesthetic Rating: {'✨' * match[4]}")
            print(f"Instagram Worthy: {'📸 Yes' if match[5] else 'Not aesthetic enough'}")
            print(f"Cover Color: {match[6]}")
            print("---")
        return matches
    except Error as e:
        print(f"Error retrieving collection: {e}")
        return []
    
def add_recipe_tags(conn, cookbook_id, tags):
    """Add tags to a cookbook (e.g., 'gluten-free', 'plant-based', 'artisanal')"""
    # Create a new tags table with many-to-many relationship
    try:
        cursor = conn.cursor()

        #check to see if user input is an existing cookbook
        cursor.execute('SELECT * FROM cookbooks WHERE id = ?', (cookbook_id,))
        match = cursor.fetchone()
        if not match:
            print(f'There was no cookbook match with id: {cookbook_id}')
            return
        
        #check to see if the cookbook already has the entered tag associated with it
        cursor.execute("SELECT cookbook_id FROM tags_table WHERE tag = ?", (tags,))
        exists = cursor.fetchone()
        #if tag isnt already entered, then add tag associated with the cookbook id to the tags table
        if not exists:
            cursor.execute('INSERT INTO tags_table(tag, cookbook_id) VALUES(?,?)', (tags,cookbook_id))
            conn.commit()
            print(f"Successfully added recipe tag with id: {cursor.lastrowid}, description: {tags}, and cookbook id: {cookbook_id}")
        else:
            print('That cookbook already has that tag associated with it.')

    except Error as e:
        print(f"Error adding tag to collection: {e}")
        return None
        
def track_borrowed_cookbook(conn, cookbook_id, friend_name, date_borrowed):
    """Track which friend borrowed your cookbook and when"""
    # Create a borrowing history table
    # Add borrowing record
    # Include return date tracking
    try:
        cursor = conn.cursor()

        #check to see if the user input matches an existing cookbook
        cursor.execute('SELECT * FROM cookbooks WHERE id = ?', (cookbook_id,))
        match = cursor.fetchone()
        if not match:
            print(f'There was no cookbook match with id: {cookbook_id}')
            return
        #check to see if the chosen cookbook is currently borrowed out and not returned
        cursor.execute("SELECT cookbook_id FROM borrow_table WHERE date_returned IS NULL AND cookbook_id=?",(cookbook_id,))
        exists = cursor.fetchone()
        #if the chosen cookbook is not currently borrowed out, then create a new borrow entry in the borrow_table to borrow the book
        if not exists:
            cursor.execute('INSERT INTO borrow_table(friend_name, date_borrowed, cookbook_id) VALUES(?,?,?)', (friend_name,date_borrowed,cookbook_id))
            conn.commit()
            print(f"Successfully entered book borrow with id: {cursor.lastrowid} cookbook id: {cookbook_id}, to: {friend_name} on: {date_borrowed}")
        else:
            print('That cookbook already has already been borrowed out.')

    except Error as e:
        print(f"Error adding tag to collection: {e}")
        return None

def main():
    # Establish connection to our artisanal database
    conn = create_connection()
    
    if conn is not None:
        # Create our free-range table
        create_table(conn)
        
        # Insert some carefully curated sample cookbooks
        cookbooks = [
            ('Foraged & Found: A Guide to Pretending You Know About Mushrooms', 
             'Oak Wavelength', 2023, 5, True, 'Forest Green'),
            ('Small Batch: 50 Recipes You will Never Actually Make', 
             'Sage Moonbeam', 2022, 4, True, 'Raw Linen'),
            ('The Artistic Toast: Advanced Avocado Techniques', 
             'River Wildflower', 2023, 5, True, 'Recycled Brown'),
            ('Fermented Everything', 
             'Jim Kombucha', 2021, 3, True, 'Denim'),
            ('The Deconstructed Sandwich: Making Simple Things Complicated', 
             'Juniper Vinegar-Smith', 2023, 5, True, 'Beige')
        ]
        
        #display all cookbooks
        print("\nCurating your cookbook collection...")
        for cookbook in cookbooks:
            insert_cookbook(conn, cookbook)
        print("\nYour carefully curated collection:")
        get_all_cookbooks(conn)

        #loop to continue running the program
        while True:
            print('1. Would you like to see all cookbooks?')
            print('2. Would you like to search cookbooks by aesthetic rating?')
            print('3. Would you like to add cookbook tags?')
            print('4. Would you like to add borrowed cookbooks?')
            print('5. Would you like to add returned books?')
            print('6. Exit')
            option = int(input("Enter your choice: "))

            #display all books again
            if (option == 1):
                print("\nYour carefully curated collection:")
                get_all_cookbooks(conn)

            #Search by aesthetic rating
            elif (option == 2):
                rating = input("\nEnter your preferred rating: ")
                search_by_aesthetic_rating(conn,rating)
            
            #add cookbook tags to a specified book
            elif (option == 3):
                cookbook_id = int(input('Enter the cookbook id number for the cookbook you would like to add a tag to: '))
                tags = input('Enter the tag you would like associated with this cookbook: ')
                add_recipe_tags(conn, cookbook_id, tags)
            
            #borrow a book to a friend
            elif (option == 4):
                print("Current borrow record: ")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM borrow_table')
                borrowed = cursor.fetchall()
                for row in borrowed:
                    print(row)
                cookbook_id = int(input('Enter the cookbook id number for the cookbook you would like to check on: '))
                friend_name = input('Enter the name of the friend that wants to borrow the book: ')
                date_borrowed = input('Enter the date that the book will be borrowed (MM/DD/YYYY): ')
                track_borrowed_cookbook(conn,cookbook_id,friend_name,date_borrowed)

            #enter returned books
            elif (option == 5):
                print("Current borrow record: ")
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM borrow_table')
                borrowed = cursor.fetchall()
                for row in borrowed:
                    print(row)
                borrow_id = int(input('Enter the borrow id number for the returned book: '))
                returned = input("Enter the date the cookbook was returned: ")
                conn.execute('UPDATE borrow_table SET date_returned = (?) WHERE borrow_id == (?)', (returned,borrow_id))
                print("Successfully entered return date")
            
            #end loop
            elif (option == 6):
                print("\nThanks for browsing!")
                break
            
            #if user doesnt choose 1-6
            else:
                print("\nInvalid choice, try again!")

        #close db connection
        conn.close()
        print("\nDatabase connection closed")
    else:
        print("Error! The universe is not aligned for database connections right now.")

if __name__ == '__main__':
    main()