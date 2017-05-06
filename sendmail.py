# Import smtplib to provide email functions
"""This file deals with mail management"""

import smtplib
import zipfile
from email.mime.application import MIMEApplication
# Import the email modules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mylib as ml  # user-defined

CONFIG = ml.read_config()

NAME = 'sendmail'
LOG_FILE = 'mail'
LOGGER = ml.init_logging(NAME, LOG_FILE)


try:

    # Define SMTP email server details
    SMTP_SERVER = CONFIG.get("SMTP", "smtp_server")
    SMTP_PORT = int(CONFIG.get("SMTP", "smtp_port"))

    # Define User details
    USER_ID = CONFIG.get("UserDetails", "UserId")
    FULL_NAME = CONFIG.get("UserDetails", "FullName")
    EMAIL_ID = CONFIG.get("UserDetails", "EmailId")
    CONTACT_NO = CONFIG.get("UserDetails", "ContactNo")

    # Define Zip details
    Z_DIRECTORY = '/var/www/logs/'
    Z_EXTRACT_PATH = '/var/www/zip/'
    Z_FILE_NAME = USER_ID + '_logs.zip'

    # Define email addresses to use
    TO_ADDRESS = CONFIG.get("SMTP", "to_Addr")

    FROM_ADDRESS = CONFIG.get("SMTP", "from_Addr")
    FROM_PASSWORD = CONFIG.get("SMTP", "from_Pass")

    MSG_SUBJECT = CONFIG.get("SMTP", "msg_Sub")

    CONFIG = ' SMTP Details > Server: ' + str(SMTP_SERVER) + ' Port:' + str(
        SMTP_PORT) + ' 	Mail Details > To: ' + str(TO_ADDRESS) + ' From:	' + str(FROM_ADDRESS) + ' Sub:	' + str(MSG_SUBJECT)
    LOGGER.warning('sendmail has started with CONFIG. >> ' + CONFIG)

    # Construct email
    MSG = MIMEMultipart('alternative')
    MSG['To'] = TO_ADDRESS
    MSG['From'] = FROM_ADDRESS
    MSG['Subject'] = MSG_SUBJECT + " : " + FULL_NAME

    # read database
    LOGGER.info('CHECK_FEEDBACK')
    #######################Query to check whether a record exists in table####
    CHECK_FEEDBACK = "SELECT COUNT(*) FROM feedback WHERE issend=0;"
    LOGGER.debug(CHECK_FEEDBACK)
    COUNT = ml.db_fetchone(CHECK_FEEDBACK)
    LOGGER.info('executed')
    LOGGER.debug('COUNT >> ' + str(COUNT))
    #######################Query to check whether a record exists in table####

    if COUNT != 0:  # records exists go with updation
        LOGGER.info('*-*Records Found*-*')

        LOGGER.info('GET_FEEDBACK')
        GET_FEEDBACK = "SELECT * FROM feedback WHERE issend=0 ORDER BY inserted_date asc;"
        LOGGER.debug(GET_FEEDBACK)
        CURSOR = ml.db_fetchall(GET_FEEDBACK)
        LOGGER.info('executed')

        ATTACH_COUNT = 0
        for row in CURSOR:
            message = row[0]
            isattach = row[1]
            time = row[2]

            LOGGER.info('Email Body')
            LOGGER.debug('message >> ' + message)
            LOGGER.debug('isattach >> ' + str(isattach))

            if isattach == 1:
                ATTACH_COUNT = ATTACH_COUNT + 1

            if ATTACH_COUNT == 1:
                CONFIG = ' Directory: ' + Z_DIRECTORY + ' Extract Path: ' + \
                    Z_EXTRACT_PATH + ' File Name: ' + Z_FILE_NAME
                LOGGER.warning(
                    'Create Zip Only Once with CONFIG. >> ' + CONFIG)

                # Zip Section
                zipf = zipfile.ZipFile(
                    Z_EXTRACT_PATH + Z_FILE_NAME, 'w', zipfile.ZIP_DEFLATED)
                ml.zipdir(Z_DIRECTORY, zipf)
                zipf.close()
                dirsize = ml.get_dirsize(Z_DIRECTORY)
                LOGGER.debug('Actual Directory Size : ' + str(dirsize))
                zipsize = ml.get_filesize(Z_EXTRACT_PATH, Z_FILE_NAME)
                LOGGER.debug('Compressed Size : ' + str(zipsize))
                LOGGER.info('executed')
                # Zip Section

            html = """\
          <html>
                    <head></head>
                    <body>
                                    <p>Hello!</p> 
                                    <p>""" + message + """</p>
                                    <p>Regards,<br>""" + FULL_NAME + """ | Beymax User <br>UserId : <b> """ + USER_ID + """</b><br>Contact : <a href="tel:""" + CONTACT_NO + """">""" + CONTACT_NO + """</a> <br>Email : <a href=""" + EMAIL_ID + """>""" + EMAIL_ID + """</a></p>                  
                    </body>
          </html>
          """
            #print (html)

            # Record the MIME types of both parts - text/plain and text/html.
            part = MIMEText(html, 'html')

            # Attach parts into message container.
            # According to RFC 2046, the last part of a multipart message, in this case
            # the HTML message, is best and preferred.

            MSG.attach(part)

            if isattach == 1:
                # This is the binary part(The Attachment):
                part = MIMEApplication(
                    open(Z_EXTRACT_PATH + Z_FILE_NAME, "rb").read())
                part.add_header('Content-Disposition',
                                'attachment', filename=Z_FILE_NAME)
                MSG.attach(part)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()

            server.login(FROM_ADDRESS, FROM_PASSWORD)
            server.sendmail(FROM_ADDRESS, TO_ADDRESS, MSG.as_string())

            print 'Email sent!'
            LOGGER.info('Email sent!')

            LOGGER.info('updatefeedback')
            updatefeedback = "UPDATE feedback SET "
            updatefeedback = updatefeedback + \
                "issend=1 , send_date = datetime('now', 'localtime') WHERE "
            updatefeedback = updatefeedback + "message='" + message + "' ;"
            LOGGER.debug(updatefeedback)
            ml.db_execquery(updatefeedback)
            LOGGER.info('executed')
            #######################Update Query#######################

        LOGGER.info('**AttachCount**')
        LOGGER.debug('ATTACH_COUNT >> ' + str(ATTACH_COUNT))
    else:
        LOGGER.info('No Records found!')

    LOGGER.warning('sendmail has stopped << ')
except:
    LOGGER.exception("got error")
    LOGGER.critical('senmail has stopped unexpectedly!!! <<')
