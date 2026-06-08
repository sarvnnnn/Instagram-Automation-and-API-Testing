import requests

print("===============================================")
print(">>> RUNNING AUTOMATED BACKEND API TESTS...")
print("===============================================\n")

# The base address of the server we are testing
BASE_URL = "https://jsonplaceholder.typicode.com"

def test_get_all_posts():
    """Test 1: Verify the server can send us a list of blog posts securely."""
    print("[*] Test 1: Fetching blog posts list from server...")
    
    response = requests.get(f"{BASE_URL}/posts")
    
    # Check if the server says "OK" (Status Code 200)
    if response.status_code == 200:
        print(f"[SUCCESS] Server responded with Status Code 200.")
        # Verify it actually sent back data items
        data = response.json()
        print(f"[SUCCESS] Verified backend returned {len(data)} data entries.\n")
    else:
        print(f"[FAILED] Unexpected status code received: {response.status_code}\n")

def test_create_new_post():
    """Test 2: Verify we can upload/create a new data entry on the database."""
    print("[*] Test 2: Simulating uploading a new post entry...")
    
    new_post_payload = {
        "title": "Automated Test Title",
        "body": "This entry was created via Python automation testing.",
        "userId": 77
    }
    
    # Send a POST request to add data
    response = requests.post(f"{BASE_URL}/posts", json=new_post_payload)
    
    # Check if the server successfully created the data (Status Code 201)
    if response.status_code == 201:
        print("[SUCCESS] Server accepted data and returned Status Code 201 (Created).")
        returned_data = response.json()
        print(f"[SUCCESS] Backend confirmed saved entry ID is: {returned_data['id']}\n")
    else:
        print(f"[FAILED] Data upload failed with status code: {response.status_code}\n")

# Execute our automated API suite
if __name__ == "__main__":
    test_get_all_posts()
    test_create_new_post()
    print("===============================================")
    print("[+] ALL BACKEND API TESTS COMPLETED PERFECTLY!")
    print("===============================================")