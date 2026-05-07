import unittest
from app import app
import os
import shutil

class AppTest(unittest.TestCase):
    def setUp(self): # runs before every test
        # Flask app set to test mode
        app.config['TESTING'] = True
        # simulate client
        self.client = app.test_client() # from Flask, creating special simulating client object for testing
        #path pointing to data directory relative to our test script
        self.data_path = os.path.join(os.path.dirname(__file__), "data")
        #create directory specified by `self.data_path`
        os.makedirs(self.data_path, exist_ok=True)

    def tearDown(self):
        #complete deletion of the directory named `data`
        shutil.rmtree(self.data_path, ignore_errors=True)

    def create_document(self, name, content=''):
        with open(os.path.join(self.data_path, name), "w") as file:
            file.write(content)

    #for signed in permissions
    def admin_session(self):
        with self.client.session_transaction() as session:
            session['username'] = 'admin'
        return self.client

    def test_index(self):
        self.create_document("about.md")
        self.create_document("changes.txt")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("about.md", response.get_data(as_text=True))
        self.assertIn("changes.txt", response.get_data(as_text=True))


    def test_file_display(self):
        self.admin_session()
        self.create_document("history.txt", "1989 - Guido van Rossum starts developing Python.")
        response = self.client.get("/history.txt")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/plain; charset=utf-8")
        self.assertIn("1989 - Guido van Rossum starts developing Python.",
                      response.get_data(as_text=True))

    def test_display_markdown(self):
        self.admin_session()
        self.create_document("about.md", "# Python is a ...")
        response = self.client.get("/about.md")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("<h1>Python is a ...</h1>", response.get_data(as_text=True))


    def test_document_not_found(self):
        self.admin_session()
        # verify redirect
        with self.client.get("/notafile.txt") as response:
            self.assertEqual(response.status_code, 302)
        # assert flash message handling
        with self.client.get(response.headers['Location']) as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("notafile.txt does not exist.", response.get_data(as_text=True))
        # assert that flash message disappears on next page load
        with self.client.get("/") as response:
            self.assertNotIn("notafile.txt does not exist.", response.get_data(as_text=True))

    def test_editing_file(self):
        self.admin_session()
        self.create_document("changes.txt")
        with self.client.get("/changes.txt/edit") as response:
            self.assertEqual(response.status_code, 200)
            self.assertIn("<textarea", response.get_data(as_text=True))
            self.assertIn('button type="submit"', response.get_data(as_text=True))

    def test_update_file(self):
        self.admin_session()
        #simulate post, <textarea name='content> in form
        with self.client.post("/changes.txt", data={'content': "new content" }) as response:
            self.assertEqual(response.status_code, 302) #verify redirect
        #verify redirect works and flash message appears
        follow_response = self.client.get(response.headers['Location'])
        self.assertEqual(follow_response.status_code, 200)
        self.assertIn("changes.txt has been updated.", follow_response.get_data(as_text=True))
        #verify file now contains submitted text
        updated_content = self.client.get("/changes.txt")
        self.assertEqual(updated_content.status_code, 200)
        self.assertIn("new content", updated_content.get_data(as_text=True))

    def test_create_file(self):
        self.admin_session()
        #verify `new` endpoint reached with correct html
        response = self.client.get("/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn('<input name="filename" id="filename"',response.get_data(as_text=True))
        #post request with new file name
        response=self.client.post("/file_upload", data={'filename':'test1.txt'})
        self.assertEqual(response.status_code, 302) # redirect
        follow_up=self.client.get(response.headers['Location']) #using header for next response object
        self.assertEqual(follow_up.status_code, 200)
        #flash message works
        self.assertIn('test1.txt has been created.', follow_up.get_data(as_text=True))
        #check that new file has been created
        last_response = self.client.get("/")
        self.assertIn('test1.txt', last_response.get_data(as_text=True))

    def test_creating_duplicate_and_empties(self):
        self.admin_session()
        #duplicates
        response=self.client.post("/file_upload", data={'filename':'test1.txt'})
        dup_response=self.client.post("/file_upload", data={'filename':'test1.txt'})
        self.assertEqual(dup_response.status_code, 422)
        self.assertIn('test1.txt already exists.', dup_response.get_data(as_text=True))
        #empties
        response=self.client.post("/file_upload", data={'filename':''})
        self.assertEqual(response.status_code, 422)
        self.assertIn('Input is required.', response.get_data(as_text=True))

    def test_delete_file(self):
        self.admin_session()
        self.create_document('test1.txt', 'testing testing')
        #deletion
        with self.client.post("/test1.txt/delete") as response:
            self.assertEqual(response.status_code, 302)
        with self.client.get(response.headers['Location']) as response:
            self.assertIn("test1.txt has been deleted.", response.get_data(as_text=True))
        with self.client.get("/") as response:
            self.assertNotIn("test1.txt", response.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
