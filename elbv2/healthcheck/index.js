const END_POINT = '/admin/swagger-ui.html';

const fetch = require('node-fetch');
const sleep = msec => new Promise(resolve => setTimeout(resolve, msec));

const AWS = require('aws-sdk'); 
AWS.config.region = 'us-east-1';

const elbv2 = new AWS.ELBv2();
const codepipeline = new AWS.CodePipeline({apiVersion: '2015-07-09'});

exports.handler = async (event, context) => {
    let jobId;
    try {
        const jobEvent = event['CodePipeline.job'];
        jobId = jobEvent ? jobEvent.id : null;
        
        console.log('start');
        const params = {
            Names: [
               "vue-sample-front-alb"
            ]
        };
        const { LoadBalancers } = await elbv2.describeLoadBalancers(params).promise();
        const { DNSName } = LoadBalancers[0];
        const endpoint = `http://${DNSName}${END_POINT}`;
        console.log(endpoint);

        let status = 0;
        do {
            var result = await fetch(endpoint);
            status = result.status;
            console.log(result);
            console.log(status);
            await sleep(3000); //wait 3s
        } while (status !== 200);

        const pipelineParams = {
            jobId
        };
        await codepipeline.putJobSuccessResult(pipelineParams).promise();

        console.log('End...');
    } catch(err) {
        const params = {
            jobId,
            failureDetails: {
              message: JSON.stringify(err.stack),
              type: 'JobFailed',
              externalExecutionId: context.invokeid
            }
        };
        await codepipeline.putJobFailureResult(params).promise();
    }
};