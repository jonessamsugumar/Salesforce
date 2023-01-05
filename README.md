# oss-request2

Step 1: Install Python

Step 2: Create a virtual environment

Step 3: Install Django

Step 4: Run the application using "python manage.py runserver" command


NOTE: External Service JSON format:

{
    "request": {
        "program": "default",
        "slug": "asdf",
        "name": "A Request",
        "owner": "Email"
    },
    "task": {
        "id": 1,
        "url": "http://asdf.com/request/asdf",
        "label": "A Task",
        "data": {
            ??
        },
        "dependencies": {
            "start": {
                "product_ecosystem": "Other",
                "relation_to_product": "Sample or Demo,
                    ...
            }
        },
        "form": {
          "product-tag-name": "Prodsec Core Adjacent Skills Group: Open Source (OSS)",
          "epic-name": "Prodsec Security Advisory",
          "subject": "[Security Advisory] OSS Request"
        },
    }
}
