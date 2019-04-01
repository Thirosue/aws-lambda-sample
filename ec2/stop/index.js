const INSTANCE_ID = 'i-0ea5ddbc554991927';

const AWS = require('aws-sdk'); 
AWS.config.region = 'us-east-1';

const ec2 = new AWS.EC2();
const codepipeline = new AWS.CodePipeline({apiVersion: '2015-07-09'});

exports.handler = async (event, context) => {
    let jobId;
    try {
        const jobEvent = event['CodePipeline.job'];
        jobId = jobEvent ? jobEvent.id : null;
        
        console.log('stop');
        const ec2Params = {
            InstanceIds: [
                INSTANCE_ID
            ]
        };
        await ec2.stopInstances(ec2Params).promise();

        const pipelineParams = {
            jobId
        };
        await codepipeline.putJobSuccessResult(pipelineParams).promise();

        context.done(null, 'Stopped Instance');
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