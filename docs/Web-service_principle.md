# Web-service principle
![image](https://user-images.githubusercontent.com/49340148/136955296-421fd326-545e-46c3-b609-3b47fcb837c6.png)

The webservice allows a customer to see current status of the project effortlessly without the need to run the software locally.
The web-service is not a required functionality of the project, but rather a convenience for the customer.

Having such service available, we shorten the feedbackloop between customer and the current implementation.
Customer can see the current implementation and report feedback right away.

It is also important that the customer understands that image processing is computationally heavy. Therefore web-service does not provide the same performance as the local development machines or the deployed machine. The web-service does not give one the same experience but tries to rather give a glimpse of how the actual deployment will feel like.

The endpoint to the web-service is https://uni-smartcanvas.herokuapp.com/

### ! Mind what you show to the camera at the web-service, it is by design insecure. !
