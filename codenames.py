import os
import sys
import time
import tkinter as tk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# Adjust the TCL and TK paths based on your working directory
if getattr(sys, 'frozen', False):
    # When running as a PyInstaller executable
    bundle_dir = sys._MEIPASS
    os.environ['TCL_LIBRARY'] = os.path.join(bundle_dir, 'tcl8.6')
    os.environ['TK_LIBRARY'] = os.path.join(bundle_dir, 'tk8.6')
else:
    # When running from source
    os.environ['TCL_LIBRARY'] = r'tcl8.6'
    os.environ['TK_LIBRARY'] = r'tk8.6'

screenshot_file = "codenames_spymaster_view_screenshot.png"  # File path to save the screenshot
background_image_path = r"backround_lofi.png"  # Full path to your background image

# Function to update the status label in tkinter
def update_status(message):
    status_label.config(text=message)
    root.update()  # Refresh the GUI immediately

# Function to reset the screenshot area and show "Future Screenshot"
def reset_screenshot_area():
    screenshot_label.config(image=screenshot_bg_tk, text="Future Screenshot")
    screenshot_label.image = screenshot_bg_tk  # Keep reference to avoid garbage collection

# Function to handle the game URL input and start Selenium
def start_game_with_url():
    global game_url
    game_url = url_entry.get()  # Get the URL from the entry field

    # Reset screenshot area before starting
    reset_screenshot_area()

    # Validate the URL
    if not re.match(r'https://codenames\.game/room/[a-zA-Z0-9\-]+', game_url):
        tk.messagebox.showerror("Invalid URL", "Please enter a valid Codenames game URL.")
        return

    update_status("Starting...")
    root.update()
    run_selenium_game()  # Call the Selenium script to run with the updated URL

# Selenium function to automate the game and take a screenshot
def run_selenium_game():
    options = Options()
    options.headless = True  # Headless mode to run browser in background
    options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"  # Adjust path if needed

    service = Service(r"geckodriver.exe")  # Path to GeckoDriver
    driver = webdriver.Firefox(service=service, options=options)

    success = False  # Flag to track if the process was successful

    try:
        # Navigate to the game room URL
        update_status("Navigating to game room...")
        driver.get(game_url)

        # Wait for the nickname input field and enter the "." nickname
        update_status("Entering nickname...")
        nickname_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "nickname-input"))
        )
        nickname_input.clear()
        nickname_input.send_keys(".")

        # Join the room
        update_status("Joining room...")
        join_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Join the Room')]"))
        )
        join_button.click()

        # Wait for 'Join as Spymaster' button and click
        update_status("Joining as Spymaster...")
        spymaster_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Join as Spymaster')]"))
        )
        spymaster_button.click()

        # Take the screenshot after a short delay
        update_status("Taking screenshot...")
        time.sleep(2.5)
        driver.save_screenshot(screenshot_file)

        # Open the Spectator menu by clicking the <p> element
        update_status("Opening Spectator menu...")
        p_element = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//p[contains(@class, 'mr-7 port:max-w-[100px] truncate')]"))
        )
        p_element.click()

        # Retry mechanism for the Spectator button
        retry_attempts = 3
        while retry_attempts > 0:
            try:
                # Wait for and click on the "Become Spectator" button
                update_status("Switching to Spectator mode...")
                spectator_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Become Spectator') and @role='button']"))
                )
                spectator_button.click()
                update_status("Switched to Spectator mode!")
                success = True  # Mark the process as successful
                break  # Exit the loop after successful click
            except Exception as e:
                retry_attempts -= 1
                update_status(f"Retrying Spectator... Attempts left: {retry_attempts}")
                time.sleep(1)  # Short delay before retry
                if retry_attempts == 0:
                    raise e  # If it fails after retries, raise the error

    except Exception as e:
        update_status(f"Error: {e}")
        return  # Exit without updating the screenshot if there's an error

    finally:
        driver.quit()
        if success:
            update_status("Loading screenshot...")
            show_screenshot()  # Show the screenshot once the browser closes
        else:
            update_status("No screenshot due to error.")

# Function to display the screenshot in tkinter
def show_screenshot():
    try:
        img = Image.open(screenshot_file)
        img = img.resize((450, 250), Image.Resampling.LANCZOS)  # Resize screenshot
        img_tk = ImageTk.PhotoImage(img)

        # Display the screenshot in the screenshot_label
        screenshot_label.config(image=img_tk, text="")  # Remove "Future Screenshot" text
        screenshot_label.image = img_tk  # Keep reference to avoid garbage collection

        # Once the screenshot is displayed, set the status to "Done!"
        update_status("Done!")

    except FileNotFoundError:
        update_status("Screenshot file not found!")
    except Exception as e:
        update_status(f"Failed to display screenshot: {e}")

# Creating the tkinter window
root = tk.Tk()
root.title("Codenames Automation")

# Set window size and disable resizing
root.geometry("500x600")
root.resizable(False, False)  # Disable resizing

# Load and blur the background image
bg_image = Image.open(background_image_path)
bg_image = bg_image.filter(ImageFilter.GaussianBlur(5))  # Blur the image
enhancer = ImageEnhance.Brightness(bg_image)
bg_image = enhancer.enhance(0.7)  # Make the background darker

# Create a tkinter-compatible background image
bg_image_tk = ImageTk.PhotoImage(bg_image)

# Background label to set the image
bg_label = tk.Label(root, image=bg_image_tk)
bg_label.place(relwidth=1, relheight=1)

# Transparent Label for asking the game URL without any background or borders
url_label = tk.Label(root, text="Enter the Codenames game URL:", font=("Helvetica", 14, "bold"), fg="black", borderwidth=0, highlightthickness=0)
url_label.pack(pady=10)

# Styled Entry field for the game URL with padding and relief to simulate depth
url_entry = tk.Entry(root, width=40, font=("Helvetica", 10), bd=3, relief="ridge", justify="center", fg="white", bg="#3a3a3a")
url_entry.pack(pady=10, padx=20)

# Darker, styled "Start" button with matching color
start_button = tk.Button(root, text="Start", font=("Helvetica", 12), bg="#3a3a3a", fg="white", activebackground="#505050", relief="ridge", command=start_game_with_url)
start_button.pack(pady=15)

# Status label for messages like "Starting..." and "Loading screenshot..."
status_label = tk.Label(root, text="", fg="blue", font=("Helvetica", 10), bg='#f0f0f0')
status_label.pack(pady=10)

# Future Screenshot area (darker background, "Future Screenshot" text)
screenshot_bg = bg_image.crop((0, 0, 450, 250))  # Crop part of the image for the screenshot area
screenshot_bg = ImageEnhance.Brightness(screenshot_bg).enhance(0.5)  # Darken more for the screenshot area
screenshot_bg_tk = ImageTk.PhotoImage(screenshot_bg)

screenshot_label = tk.Label(root, image=screenshot_bg_tk, text="Future Screenshot", font=("Helvetica", 12), compound="center", width=450, height=250, relief="ridge", bd=3)
screenshot_label.pack(pady=20)

# Start the tkinter main loop
root.mainloop()
