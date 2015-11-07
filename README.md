# probase
Python Apis for PoolClues
Test server for front end setup at http://188.166.249.229:8080/
so use it as url in front end.
NOTE: This ip address is blocked in college so use proxy to access it in college

To test if you are apble to connect to server send http get request to http://188.166.249.229:8080/ or try to open it in browser

response should be
               {
               "success": "It works"
               }

#Api description:
## Register User
### endpoint: `/register`
so url will be `http://188.166.249.229:8080/register`

### Samle payload:
               {
                "first_name": "Gaurav",
               "middle_name":"Ramakant",
               "last_name": "Shukla",
               "email_id":"deathping1994@gmail.com",
               "password":"bastard007",
               "house_no":"559 ka/48 kha",
               "street":"Singar Nagar",
               "city":"Lucknow",
               "state":"Uttar Pradesh",
               "country":"India",
               "phone":"8375847862"     //optional
               }

### Response:  
              {
                 "success": "User successfully registered"
             }
        or
             {
             "error": "Oops something went wrong. Contact the adminsitrator"
             }

## Verify Email
### endpoint: `/:email:/verify`
so url will be `http://localhost:8080/gshukla66@gmail.com/verify`

### Samle payload:
              {
             "authtoken": "$2b$12$WI1yg7EgIo0MbGblJd7sA.zhaPBSpMuKenvnoWEiiUANR1ywBOEaC",
             "verification_code":"7OL124"
              }
              
### Response:  
             {
                "success": ""Email Successfully verified"
            }
        or
            {
            "error": "Some error message"
            }


## Product List
### endpoint: `/products/list`
so url will be `http://localhost:8080/products/list`

### Samle payload:
              {
             "authtoken": "$2b$12$WI1yg7EgIo0MbGblJd7sA.zhaPBSpMuKenvnoWEiiUANR1ywBOEaC"
              }
              
### Response:  
                {
            "products": [
                        {"name":"product name",
                        "image":"http://img.com/img1.jpg",
                        "price":100,
                        "id":123Hj
                        },
                        {"name":"product name",
                        "image":"http://img.com/img1.jpg",
                        "price":100,
                        "id":1123Hj
                        }
                        ]
                    }
                or
                {
                "error": "Some error message"
                }



## Forgot Password
### endpoint: `/forgotpassword/:user:`
so url will be `http://localhost:8080/forgotpassword/gshukla66@gmail.com`

### Response:  
                {
                   "success": "Password change request has been recorded check your email for further instructions."
               }
            or
               {
               "error": "Some error message"
               }


### endpoint: /authenticate
example: http://188.166.249.229:8080/logout/gshukla66@gmail.com

#### payload:
                   {
                   "email_id":<user's email_id>,
                   "password":<user's password>
                   }
### Response:
               {
               "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq",
               "success": "Successfully Logged in !"
               }
               or
               {
               "error":"Some error message"
               }
        

### endpoint: /logout/:email_id:
example: http://188.166.249.229:8080/logout/gshukla66@gmail.com

#### payload:
               {"authtoken":<user's suth token>
               }
### Response:
               {
               "success":"Successfully logged off"
               }
               or
               {
               "error":"Some error message"
               }
NOTE: As of now this endpoint return successfully logged off even when you are not logged in , this is a bug but wont be fixed keeping in mind that this system would be replaced with three legged auth system using redis,and JWT


### endpoint: /:email_id:/addphone/:phonenumber:
example: http://188.166.249.229:8080/gshukla66@gmail.com/addphone/8375847862

#### payload:
           {"authtoken":<user's suth token>
           }
### Response:
           {
           "success":"Contact added Successfully!"
           }
           or
           {
           "error":"Some error message"

           }

### endpoint: /:email_id:/event/list/:type:

type can be invited, all, created
invited : List all events the user is invited in
created : List all events user has created
all : Include both created and invited
 example: http://188.166.249.229:8080/gshukla66@gmail.com/event/list/invited

### Response:

               {
            "event_list": [
             {
                 "date_created": "2015-10-08",
                 "event_description": "Too lazy for that",
                 "event_id": 106,
                 "event_name": "Gaurav's b'day",
                 "public": true,
                 "target_amount": 5000,
                 "target_date": "2015-12-11"
             },
             {
                 "date_created": "2015-10-08",
                 "event_description": "Too lazy for that",
                 "event_id": 106,
                 "event_name": "Gaurav's b'day",
                 "public": true,
                 "target_amount": 5000,
                 "target_date": "2015-12-11"
             },
             {
                 "date_created": "2015-10-08",
                 "event_description": "Too lazy for that",
                 "event_id": 106,
                 "event_name": "Gaurav's b'day",
                 "public": true,
                 "target_amount": 5000,
                 "target_date": "2015-12-11"
             }
            ]
            }          or
                {
                "error":"Some error message"
                }
           
            
### endpoint: /event/:event_id:

example: http://188.166.249.229:8080/event/115

### Response:
       {
           "event_description": "Too lazy for that",
           "event_id": 115,
           "event_name": "Gaurav's b'day",
           "target_amount": 5000,
           "target_date": "2015-12-11"
       }
       or
       {
       "error":"Some error message"
       }
### endpoint: /event/create
example: http://188.166.249.229:8080/event/115

### Payload:
          {"email_id":"94@gmail.com",
            "event_name": "Gaurav's b'day",
            "target_date": "11122015",
            "target_amount":"5000",
            "description":"Too lazy for that",
            "invites": [{"email_id":"deathping1994@gmail.com"}
                ],
            "products":["id1","id2"],  //Array of pid of products selected as gift (optional in case of cash voucher do not pass this field)
    
            "msg": "new custom message",
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq",
            "public": true
    
          }
### Response:
       {
           "event_id": 115,
           "success": "event created successfully"
       }
       or
       {
       "error":"Some error message"
       }


### endpoint: /:user:/change/password
example: http://188.166.249.229:8080/gshukla66@gmail.com/change/password

### Payload:
          {
            "request_code":"password change request code sent in email".
            "new_password":"new password"
          }
### Response:
       {
           "success": "Password changed successfully"
       }
       or
       {
       "error":"Some error message"
       }


### endpoint: /event/:eventid:/invite
example: http://188.166.249.229:8080/event/104/invite
### Payload:
          {
            "invites": [{"email_id":"deathping1994@gmail.com","amount":2000}
                ],
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq"
          }
### Response:
       {
           "success": "Invites sent successfully"
       }
       or
       {
       "error":"Some error message"
       }


### endpoint: /:emailid:/pay/:eventid:
example: http://188.166.249.229:8080/gshukla66@gmail.com/change/password

### Payload:
          {
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq"
          }
### Response:
       {
           "success": "Payment request submitted check status in the payment history"
       }
       or
       {
       "error":"Some error message"
       }

# Wallet

## Transaction History

Shows list of all transaction by a particular user. Where pool_id ='' in response then the money was added to wallet.
if pool_id=event id or registry id 

### endpoint: /:emailid:/wallet/history
example: http://188.166.249.229:8080/gshukla66@gmail.com/wallet/history

### Payload:
          {
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq"
          }
### Response:
       {
            "transactions": [
                {
                    "amount": 0,
                    "date": "2015-11-04",
                    "pool_id": "",
                    "transaction_id": "$2b$12$C1Ba/kQF3jhBNNdKpzUy6uCPGRTRym0/SCgA.48Cr463G0nxOHMSm"
                },
                {
                    "amount": 400,
                    "date": "2015-11-04",
                    "pool_id": "",
                    "transaction_id": "$2b$12$Q9yqx80LPuDBX3KCL9x0Y.Bn8T/gNplTzD2YnNvcEVYUm.Zlq8aqa"
                }
            ]
        }
       or
       {
       "error":"Some error message"
       }


## Dummy Payment (Add money to wallet)

Each user is given a wallet when he signs up all the payments are processed via this wallet. Initially the balance is zero
to add money to wallet user needs to be logged in and then submit a request to add money to wallet via this url.

### endpoint: /:emailid:/wallet/add
example: http://188.166.249.229:8080/gshukla66@gmail.com/wallet/add

### Payload:
          {
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq",
            "amount": 5000
          }
### Response:
       {
           "success": "Payment request submitted check status in the payment history"
       }
       or
       {
       "error":"Some error message"
       }

## Change Password without forgot password

### endpoint: /:user:/change/password/2
example: http://188.166.249.229:8080/gshukla66@gmail.com/change/password/2

### Payload:
          {
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq",
            "new_password": "new password here"
          }
### Response:
       {
           "success": "Password updated successfully"
       }
       or
       {
       "error":"Some error message"
       }

# Event Registry

Registry is like wish list of user. User creates a registry and selects products which he wants to receive as gifts. 
Invite is send to all email id from whom user wishes to get a gift.
User is not bound to make any payment and only this products get delivered for which the payment is complete

## Create Registry

### end point : /registry/create
example: http://188.166.249.229:8080/registry/create

### Payload:
          {
            "email_id":"deathping1994@gmail.com",
            "registry_name": "Gaurav's b'day",
            "target_date": "11122015",
            "description":"Too lazy for that",
            "invites": [{"email_id":"poolclues@gmail.com","amount":3000
            }],
            "products":["id1","id2"], 
            "msg": "new custom message",
            "authtoken": "$2b$12$zXJud8qrfsPbMjdyLULT7O13LsrJ.LfO5RwwxrpCvy3cuSyrqXPqS",
            "public": true   //optional By default Assumed too be true

            }
### Response:
           {
               "failedlist": [],
                "inviteSent": true,
                "registry_id": 105,
                "success": "Registry created successfully."
            }
           or
           {
           "error":"Some error message"
           }

## Invite in Registry
### endpoint: /registry/:registry_id:/invite
example: http://188.166.249.229:8080/registry/104/invite
### Payload:
          {
            "invites": [{"email_id":"deathping1994@gmail.com","amount":2000}
                ],
            "authtoken": "$2a$12$wdss4GzgeKb/JW/HUpINjO0pZ462LF65U2dBnlHAGmF7TIndhdRgq"
          }
### Response:
       {
           "success": "Invites sent successfully"
       }
       or
       {
       "error":"Some error message"
       }
