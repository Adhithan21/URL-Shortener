import streamlit as st
import requests

# Backend service URL
BASE_URL = "http://127.0.0.1:5000"  # Ensure this matches the backend's URL and port

st.title(":blue[URL Shortener]")

# Menu for choosing between features
menu = st.radio("Choose an action:", ["Shorten URL", "Redirect URL"])

if menu == "Shorten URL":
    st.subheader(":red[Shorten a Long URL]")
    
    # Input fields for URL and optional custom alias
    original_url = st.text_input("Enter the original long URL:")
    custom_alias = st.text_input("Enter a custom alias (optional):")
    
    if st.button("Shorten"):
        if not original_url.strip():
            st.error("Please enter a valid long URL.")
        else:
            data = {"url": original_url}
            if custom_alias.strip():
                data["custom_alias"] = custom_alias.strip()
            
            try:
                response = requests.post(f"{BASE_URL}/shorten", json=data)
                if response.status_code == 201:
                    short_url = response.json().get("short_url")
                    st.success(f"Shortened URL: {BASE_URL}/{short_url}")
                else:
                    st.error(response.json().get("error", "An unexpected error occurred"))
            except requests.exceptions.RequestException:
                st.error("Unable to connect to the backend service. Please try again later.")

elif menu == "Redirect URL":
    st.subheader("Redirect from a Shortened URL")
    
    # Input field for the short URL or alias
    short_url = st.text_input("Enter the shortened URL or alias:")
    
    if st.button("Redirect"):
        if not short_url.strip():
            st.error("Please enter a valid shortened URL or alias.")
        else:
            # Extract alias if a full URL is entered
            alias = short_url.strip().split('/')[-1]
            full_url = f"{BASE_URL}/{alias}"
            
            try:
                response = requests.get(full_url, allow_redirects=False)
                if response.status_code == 302:  # HTTP redirection
                    redirect_url = response.headers.get("Location")
                    st.success(f"Redirecting to: {redirect_url}")
                else:
                    st.error("Shortened URL not found!")
            except requests.exceptions.RequestException:
                st.error("Unable to connect to the backend service. Please try again later.")
                # Display a hint to try a custom URL
                st.info("Hint: You can also try typing a custom URL alias, for example, 'short.ly/abc123'.")
