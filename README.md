# **CS50 Final Project - YouTube Video Downloader Web Application**

Welcome to the repository for my CS50 Final Project: a web-based YouTube Video Downloader. This application is designed to efficiently download videos from YouTube, offering a seamless and user-friendly experience. Users can choose various formats and video qualities, track the download progress in real-time, and manage their download history. Below is an overview of the project’s features, technical details, and instructions for running it locally.

---

## ⚠️ **Important Disclaimer**

This project is intended **for academic purposes only**. The application should not be used in violation of YouTube’s Terms of Service. Downloading YouTube videos without permission may breach YouTube’s copyright policies and terms of use. Please ensure that you have the right to download any content before using this tool.

---

## **Video Preview**

[![YouTube Video Downloader Preview](https://img.youtube.com/vi/gVoWQ8rKb28/0.jpg)](https://www.youtube.com/watch?v=gVoWQ8rKb28)

---

## **Key Features**

### **1. Video Download & Format Selection**
The application allows users to download videos from YouTube by simply entering the video URL. Users can choose from multiple formats, including MP4 and MP3, and different quality options (e.g., 1080p, 720p).

### **2. Progress Tracking**
A real-time progress bar tracks the status of each download, enhancing the user experience by providing transparency on the download's progress. This feature was implemented using JavaScript and asynchronous communication with the backend.

### **3. MP3 File Integration**
Unique to this application is the ability to open downloaded MP3 files directly within Apple Music. This required precise handling of file formats and integration with operating system behaviors.

### **4. User Account Management**
The application includes a full user authentication system, allowing users to create accounts, reset passwords, and receive email notifications when their downloads are complete. This feature integrates secure user data handling and email server configuration.

### **5. Download History**
Users can view and manage their previous downloads through their accounts. This required designing an efficient database schema to store and retrieve download history.

### **6. Contact & Support**
A “Contact Us” form allows users to submit inquiries or support requests directly through the app, providing an additional layer of interactivity and user engagement.

---

## **Technologies Used**

- **Backend**: Flask for handling requests and `pytube` for managing video downloads and conversions.
- **Frontend**: HTML, CSS (Bootstrap for responsive design), and JavaScript for dynamic behavior and real-time updates.
- **Database**: SQLite (or another relational database) for managing user accounts and download history.
- **User Authentication**: Flask-Login for secure user management and session handling.
- **API Integration**: YouTube video download functionality powered by the `pytube` library.

---

## **Project Structure**

- **`/templates/`**: Contains HTML templates for each of the application's pages, including the homepage, login, download history, and contact page.
- **`/static/`**: Houses static assets such as CSS (for styling), JavaScript (for interactivity), and images.
- **`app.py`**: The main Flask application file that handles routing, user requests, and video download logic.
- **`models.py`**: Contains the database models, including user information and download history.
- **`utils.py`**: Utility functions for handling video downloads, format conversions, and progress tracking.

---

## **Installation & Setup**

To run the web application, follow these steps:

1. **Install Python 3.12.0:**
   Ensure that Python version 3.12.0 is installed on your system. You can download it from the [official Python website](https://www.python.org/downloads/).

2. **Install Dependencies:**
   Navigate to the project directory and install the required Python packages using the `requirements.txt` file:
   ```bash
   pip install -r requirements.txt
3. **Navigate to the Project Directory:**
   Change to the project directory containing the manage.py file:
   ```bash
   cd download
4. **Create a Superuser Account:**
   Execute the following command to create a superuser account with administrative privileges:
   ```bash
   python3 manage.py createsuperuser
5. **Run the Development Server:**
   Start the Django development server to launch the application:
   ```bash
   python3 manage.py runserver
6. **Access the Application:**
   Open your web browser and navigate to the provided local server URL (usually http://127.0.0.1:8000/).
7. **Update pytube:**
   Lastly, it is important to keep pytube up to date. If any problems arise, please refer to this (https://github.com/pytube/pytube/issues/1973#issuecomment-2281113019)
   
By following these steps, you will be able to set up and run the web application on your local machine, allowing you to utilize its features and functionalities.

## Conclusion

This web application represents a significant advancement in the functionality and usability of video download tools. Its distinctive features, user-friendly design, and comprehensive functionality make it a valuable asset for managing and accessing YouTube video content. If you have any questions or require support, please use the "Contact Us" form available within the application. Thank you for exploring my project!