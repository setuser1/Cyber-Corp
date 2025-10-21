# Article:

## Check commits for more!
https://www.engadget.com/big-tech/amazons-aws-outage-has-knocked-services-like-alexa-snapchat-fortnite-venmo-and-more-offline-142935812.html?src=rss

Big tech

Amazon's AWS outage knocked services like Alexa, Snapchat, Fortnite, Venmo and more offline

A massive outage highlights why relying on a few companies to power much of the internet is far from ideal.

Kris Holt

Contributing Reporter

Kris HoltContributing Reporter

Updated Tue, October 21, 2025 at 1:21 AM UTC

5 min read

SOPA Images via Getty Images

It felt like half of the internet was dealing with a hangover from the morning of October 19 to the early hours of October 20. A severe Amazon Web Services outage took out many, many websites, apps, games and other services that rely on Amazons cloud division to stay up and running. That included a long list of popular software like Venmo, Snapchat, Canva and Fortnite. Even Amazon's own assistant Alexa stuttered, and if you were wondering why the internet seemed to be against you — you weren't imagining it. The good news is that, Amazon announced by 6:53PM Eastern time on October 20 that it resolved the "increased error rates and latencies for AWS Services."

The company said it "identified the trigger of the event as DNS resolution issues for the regional DynamoDB service endpoints." It ran into more problems as it tried to solve the outage, but it was eventually able to fix everything. "By 3:01 PM, all AWS services returned to normal operations," it said.

At about 4:30PM ET on October 20, things seemed to be returning back to normal. Apps like Venmo and Lyft, which were either slow to respond or completely nonresponsive before, were appearing to behave smoothly.

Advertisement

Advertisement

Advertisement

As of 1:15PM ET on October 20, multiple services were unavailable, including asking Alexa for the weather or to turn off lights in your home. The Lyft app was also slower to respond than usual, and Venmo transactions were not completing.

According to the AWS service health page at the time, Amazon was looking into "increased error rates and latencies for multiple AWS services" in the US-EAST-1 region (i.e. data centers in Northern Virginia) as of 3:11AM ET on Monday. By 5:01AM, AWS had figured out that a DNS resolution issue with its DynamoDB API was the cause of the outage. DynamoDB is a database that holds info for AWS clients.

At about 12:08PM ET, the company posted a small statement that reiterated the above and added that the "underlying DNS issue was fully mitigated at 2:24 AM PDT." According to the notice, some Amazon "customers still continue to experience increased error rates with AWS services in the N. Virginia (us-east-1) Region due to issues with launching new EC2 instances." Amazon also said Amazon.com and Amazon subsidiaries, as well as AWS customer service support operations have been impacted.

“Amazon had the data safely stored, but nobody else could find it for several hours, leaving apps temporarily separated from their data,” Mike Chapple, a teaching professor of IT, analytics and operations at University of Notre Dame, told CNN. “Its as if large portions of the internet suffered temporary amnesia.”

Advertisement

Advertisement

Advertisement

As of 6:35AM, AWS said it had fully mitigated the DNS issue and that "most AWS Service operations are succeeding normally now." However, the knock-on effect caused issues with other AWS services, including EC2, a virtual machine service on which many companies build online applications.

At 8:48AM, AWS said it was "making progress on resolving the issue with new EC2 instance launches in the US-EAST-1 Region." It recommended that clients not tie new deployments to specific Availability Zones (i.e. one or more data centers in a given region) "so that EC2 has flexibility" in picking a zone that may be a better option.

At 9:42AM, Amazon noted on the status page that although it had applied "multiple mitigations" across several Availability Zones in US-EAST-1, it was "still experiencing elevated errors for new EC2 instance launches." As such, AWS was "rate limiting new instance launches to aid recovery." The company added at 10:14AM that it was seeing "significant API errors and connectivity issues across multiple services in the US-EAST-1 Region." Even once all the issues are resolved, AWS will have a significant backlog of requests and other factors to process, so it'll take some time for everything to recover.

Many, many, many companies use US-EAST-1 for their AWS deployments, which is why it felt like half of the internet was knocked offline on Monday morning. As of mid-morning, tons of websites and other services were sluggish or offering up error messages. Outage reports for a broad swathe of services spiked on Down Detector. Along with Amazon's own services, users reported issues with the likes of banks, airlines, Disney+, Snapchat, Reddit, Lyft, Apple Music, Pinterest, Fortnite, Roblox and The New York Times — sorry to anyone whose Wordle streaks may be at risk.

Advertisement

Advertisement

Advertisement

Sites like Reddit have posted their own status updates, and though they don't explicitly mention AWS, it's possible that the services' paths may cross somewhere in the pipelines.

AWS offers a lot of useful features to clients, such as the ability for websites and apps to automatically scale compute and server capacity up and down as needed to handle ebbs and flows in traffic. It also has data centers around the world. That kind of infrastructure is attractive to companies that serve a global audience and need to stay online around the clock. As of mid-2025, it was estimated that AWS' share of the worldwide cloud infrastructure market was 30 percent. But incidents such as this highlight that relying on just a few providers to be the backbone of much of the internet is a bit of a problem.

Update October 20, 2025, 9:21PM ET: This story has been updated with Amazon's latest update that says the issue has been resolved.

Update, Oct 20 2025, 10:57AM ET: This story has been updated to include a short list of services affected in the intro.

Advertisement

Advertisement

Advertisement

Update, Oct 20 2025, 11:17AM ET: This story has been updated to include a reference to Reddit's own status update website.

Update, Oct 20 2025, 1:15PM ET: This story has been updated to include a paragraph reflecting the status of popular services like Lyft, Venmo and Alexa, based on our editors' personal experiences as of this time.

Update, Oct 20 2025, 3:15PM ET: This story has been updated to include a short statement from Amazon describing a timeline of events, when the underlying issue was mitigated and what parts of Amazon have been impacted.

Update, Oct 20 2025, 4:30PM ET: This story has been updated to reflect the status of services like Venmo and Lyft as of Monday afternoon.

Advertisement

About our ads