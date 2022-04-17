# Planning

Sign up/Login process
Private chats
Chat history
OS UI

## Sign up/Login process

- database
    email
    firstName
    lastName
    nickName
    password (encrypted)
    icon

- UI
    password complexity validation
    captcha
    email validation (syntax) - send validation email
    MFA (create, reset)
    Forgot password
    Remember me
    icon

## Private chats

- UI
    - left side split
        - left side up
            All users
            Online users shown first
            user search bar

        - left side down
            Private chats if exist
            Main chat room link

    - right side
        default main chat window
        replaced by private chat if selected

    - right side up
        profile icon
            when clicked
                edit details
                change password
                reset MFA
                change icon
                logout

    - chat window ui
        - text area (bottom)
            Send on Enter
            Drop line on Shift Enter
            share button
            emoji select button
            gif button
            send random pornhub link button

        - chat area
            each message has bubble
            time/date split
            expand images and links
            select message - copy
            select message - reply
