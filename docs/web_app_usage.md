# How to use the current implementation of the cPouta web app

You can access the SmartCanvas application from

[SmartCanvas](http://86.50.228.113:5000/)

[chrome::/flags](chrome://flags/#unsafely-treat-insecure-origin-as-secure)
# Camera not showing?

In the case of the camera feed not showing, you need to do the following:

- Make sure you are using Google Chrome browser
- Visit this address with the browser: [chrome::/flags](chrome://flags/#unsafely-treat-insecure-origin-as-secure)
- Add http://86.50.228.113:5000/ to the text box and change the setting to 'Enabled'
    -  (Note: replace http://86.50.228.113:5000/ with the new address if you need to deploy the application to a new cPouta instance)
- Relaunch the browser and now the SmartCanvas app should ask for permission to use the camera

We have to do this because the service is running with HTTP-protocol and Chrome doesn't allow video sharing over this protocol due to privacy and security issues. Since our service is running on CSC provided virtual server and the program itself is dockerized it should be sufficiently secure to allow camera sharing. User discretion is still advised and this method should only be used in development environments.
