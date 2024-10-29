# Forum-Project-Stage-CC
Forum Project Stage CC Template Repo

**Project Vision Statement:**

*"Empowering Innovation: Bridging Startups and Investors for Ukraine's Economic Growth"*

**Overview:**

In the dynamic world of entrepreneurship, the path from a transformative idea to a successful venture is often complex and challenging. Our WebAPI application, developed using the Django Rest Framework, is designed to be a cornerstone in simplifying this journey. We aim to create a robust and secure digital platform that caters to two pivotal groups in the business ecosystem: innovative startups with compelling ideas and forward-thinking investors seeking valuable opportunities.

**Goals:**

1. **Fostering Collaborative Opportunities:** Our platform bridges startups and investors, enabling startups to showcase their groundbreaking proposals and investors to discover and engage with high-potential ventures.

2. **Seamless User Experience:** We prioritize intuitive navigation and interaction, ensuring that startups and investors can easily connect, communicate, and collaborate.

3. **Secure and Trustworthy Environment:** Security is at the forefront of our development, ensuring the confidentiality and integrity of all shared information and communications.

4. **Supporting Economic Growth:** By aligning startups with the right investors, our platform not only cultivates individual business success but also contributes significantly to the growth and diversification of Ukraine's economy.

**Commitment:**

We are committed to delivering a platform that is not just a marketplace for ideas and investments but a thriving community that nurtures innovation fosters economic development, and supports the aspirations of entrepreneurs and investors alike. Our vision is to see a world where every transformative idea has the opportunity to flourish and where investors can confidently fuel the engines of progress and innovation.

![image](https://github.com/mehalyna/Forum-Project-Stage-CC/assets/39273210/54b0de76-f6e3-4bf3-bf38-fb5bf1d1d63d)



### Basic Epics

0. **As a user of the platform**, I want the ability to represent both as a startup and as an investor company, so that I can engage in the platform's ecosystem from both perspectives using a single account.

   - Features:
     - implement the functionality for users to select and switch roles.

2. **As a startup company,** I want to create a profile on the platform, so that I can present my ideas and proposals to potential investors.
   
   - Features:
     -  user registration functionality for startups.
     -  profile setup page where startups can add details about their company and ideas.

3. **As an investor,** I want to view profiles of startups, so that I can find promising ideas to invest in.
   
   - Features:
     -  feature for investors to browse and filter startup profiles.
     -  viewing functionality for detailed startup profiles.

4. **As a startup company,** I want to update my project information, so that I can keep potential investors informed about our progress and milestones.
   
   - Features:
     -  functionality for startups to edit and update their project information.
     -  system to notify investors about updates to startups they are following.

5. **As an investor,** I want to be able to contact startups directly through the platform, so that I can discuss investment opportunities.
   
   - Features:
     -  secure messaging system within the platform for communication between startups and investors.
     -  privacy and security measures to protect the communication.

6. **As a startup company,** I want to receive notifications about interested investors, so that I can engage with them promptly.
   
   - Features:
     -  notification functionality for startups when an investor shows interest or contacts them.
     -  dashboard for startups to view and manage investor interactions.

7. **As an investor,** I want to save and track startups that interest me, so that I can manage my investment opportunities effectively.
   
   - Features:
     -  feature for investors to save and track startups.
     -  dashboard for investors to manage their saved startups and investment activities.

### Additional Features

- **Security and Data Protection**: Ensure that user data, especially sensitive financial information, is securely handled.
  
- **User Feedback System**: Create a system for users to provide feedback on the platform, contributing to continuous improvement.

- **Analytical Tools**: Implement analytical tools for startups to understand investor engagement and for investors to analyze startup potential.

### Agile Considerations

- Each user story can be broken down into smaller tasks and developed in sprints.
- Regular feedback from both user groups (startups and investors) should be incorporated.


### Virtual Environment Setup
```shell
python3 -m venv .venv
```

```shell
source .venv/bin/activate
```

```shell
pip3 install -r requirements.txt
```

### Create New Project
```shell
django-admin startproject forum
```

### Run Server
```shell
cd forum && python3 manage.py runserver
```

### Environment
Prepare *.env* file containing sensitive info
```text
SECRET_KEY=your_secret_key
DEBUG=(boolean value)
DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=your_database_host
DATABASE_PORT=your_database_port 
```

### Migrations
```shell
cd forum && python manage.py makemigrations
```

```shell
cd forum && python manage.py migrate
```

## Code Quality
We use Pylint for static code analysis to maintain code quality and consistency.

### Installation
Make sure to install the required dependencies:
pip install -r requirements.txt

### Run pylint
To run Pylint on a specific app, use:
pylint --load-plugins pylint_django [your_django_app_folder]

### Create Super User
```shell
cd forum && python manage.py createsuperuser
```

## Communication
### Get token
http://localhost:8000/api/token/

### Create conversation
```shell
curl --location 'http://127.0.0.1:8000/api/conversations/' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NTQxOTI3LCJpYXQiOjE3Mjk1NDEwMjcsImp0aSI6IjI1MzM0Mjc1MDYzNDQ0MDU4MDkxNjFmOWNlNzBkMjQ0IiwidXNlcl9pZCI6IjcyZjgwZGEyLTU2ZDMtNDZhNS05NTBiLThmM2VkMzU1ZjUxZCJ9.nBjpzkWJaM_PIW7aY1Zw-7JlmldLjO44x2yQpvSmmd4' \
--data '{
    "participants": ["fc22603d-0f5d-4ac2-8964-b073e783abc8"]
}'
```

### Send message
```shell
curl --location 'http://127.0.0.1:8000/api/conversations/6712520301fa3c40d55e0683/messages' \
--header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI5NTQxOTI3LCJpYXQiOjE3Mjk1NDEwMjcsImp0aSI6IjI1MzM0Mjc1MDYzNDQ0MDU4MDkxNjFmOWNlNzBkMjQ0IiwidXNlcl9pZCI6IjcyZjgwZGEyLTU2ZDMtNDZhNS05NTBiLThmM2VkMzU1ZjUxZCJ9.nBjpzkWJaM_PIW7aY1Zw-7JlmldLjO44x2yQpvSmmd4'
```

### Subscribe to messages
```
ws://127.0.0.1:8000/ws/communications/6712520301fa3c40d55e0683/
```


## Frontend
Instructions for Installing React, Dependencies, and Running the React Server

Navigate to the Frontend Directory:First, ensure you are inside the frontend directory where the React project is located: 

cd frontend

Install Dependencies:Once you're in the frontend directory, install the required dependencies specified in the package.json file. This will include packages like React, Axios, React Router:

npm install

This command will read the package.json file and install all necessary libraries and tools for the project.
Run the React Development Server:After the dependencies have been installed, you can start the React development server using:

npm start

The React development server will now run on http://localhost:3000. This server serves the frontend, while the Django API should be running on http://localhost:8000.


