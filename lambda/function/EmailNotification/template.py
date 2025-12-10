html_template = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8"/>
        <title>File Uploaded</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f7f9fc;
                color: #333333;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 8px;
                padding: 30px;
                max-width: 600px;
                margin: auto;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
            }}
            .title {{
                font-size: 20px;
                font-weight: bold;
                color: #1a73e8;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
            }}
            .content {{
                font-size: 16px;
                line-height: 1.6;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 12px;
                color: #888888;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="title">
                <span class="check-icon">{status_icon}</span>
                {header}
            </div>
            <div class="content">
                {message}
                <br/><br/>
                Drive Name: {drive_name}<br/>
                File Name: {file_name}<br/>
                Uploaded on: {date}
                <br/><br/>
                Please <a href="{link}" target="_blank">click here</a> to check the application.
                <br/><br/>
                Thank you,<br/>
                OM Basic Input Data Team
            </div>
            <div class="footer">
                {footer}
            </div>
        </div>
    </body>
</html>
"""