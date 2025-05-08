## Issues with GDPR

Smartcanvas is not currently GDPR compliant.

As per the legislation (https://gdpr-info.eu/art-4-gdpr/), personal data includes the face of the person and doing image manipulation with your face is processing (adaptation or alteration) personal data. This means that the user will need to accept GDPR, even if we don’t save their face. It would seem that even temporarily storing the face in RAM wouldn’t be GDPR compliant, as we would still be processing personal information. The app deletes (as of 3.5.25) the faces/altered faces of people after the QR code countdown has passed, so no information *should* be saved.

As of May 2025 SmartCanvas
* DOES process personally identifiable information
  * Face and other features visible to the camera
  * Camera frame in-memory for around 8 to 40 milliseconds when identifying landmarks 
  * Filtered picture in-memory for 180 seconds after taking a picture
* MIGHT process PII on a non-local device
  * Depending on deployment details, the pictures may be transmitted securely with TLS encryption to a remote host running SmartCanvas
* DOES NOT
  * Transmit images unencrypted
  * Store images on non-volatile storage
  * Store PII for longer than 180 seconds
  * Store PII without user interaction

Relevant legislation is here:

*‘personal data’* 
_means any information relating to an identified or identifiable natural person (‘data subject’); an identifiable natural person is one who can be identified, directly or indirectly, in particular by reference to an identifier such as a name, an identification number, location data, an online identifier or to one or more factors specific to the physical, physiological, genetic, mental, economic, cultural or social identity of that natural person;_

*‘processing’*
_means any operation or set of operations which is performed on personal data or on sets of personal data, whether or not by automated means, such as collection, recording, organisation, structuring, storage, adaptation or alteration, retrieval, consultation, use, disclosure by transmission, dissemination or otherwise making available, alignment or combination, restriction, erasure or destruction;_

Consent needs to be a “clear affirmative action”, and in the past Smartcanvas asked for a thumbs up to accept GDPR. However, what constitutes a “thumbs up” was defined by programming logic and affected by camera quality and thus cannot be guaranteed to be robust enough for legal consent.

*‘consent’*
_of the data subject means any freely given, specific, informed and unambiguous indication of the data subject’s wishes by which he or she, by a statement or by a clear affirmative action, signifies agreement to the processing of personal data relating to him or her;_
