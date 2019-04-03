const INSTANCE_ID = 'i-0ea5ddbc554991927';
const SLACK_WEBHOOK_URL = 'https://hooks.slack.com/services/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';

const fetch = require('node-fetch');
const post = (url, data) => {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });
};

const AWS = require('aws-sdk'); 
AWS.config.region = 'us-east-1';

const ec2 = new AWS.EC2();
const codebuild = new AWS.CodeBuild({apiVersion: '2016-10-06'});
const s3 = new AWS.S3();

exports.handler = async (event, context) => {
    console.log('--------------------- start e2e end funcition ....');
    console.log(event);
    
    //----------------  Stop e2e run instance
    console.log('1. Stop e2e Instance !');
    const ec2Params = {
        InstanceIds: [
            INSTANCE_ID
        ]
    };
    await ec2.stopInstances(ec2Params).promise();

    //----------------  Start Stack Destroy (by terraform)
    console.log('2. Stack Destroy Start !');
    const buildParams = {
      projectName: 'vue-sample-destroy-for-e2e'
    };
    await codebuild.startBuild(buildParams).promise();

    //----------------  Post e2e result
    console.log('3. Post Slack !');
    // get current report date
    const param = {
        Bucket: "vue-sample-e2e-results",
    };
    const { Contents } = await s3.listObjects(param).promise();
    const target = Contents.map(list => list.Key.split('/')[0]).sort((a,b)=>a-b).pop();
    console.log(`target timestamp : ${target}`);
    
    const s3BaseUrl = `https://s3.amazonaws.com/vue-sample-e2e-results/${target}`;
    const { stats } = await fetch(`${s3BaseUrl}/mochawesome.json`).then(res => res.json());
    let slackPost;
    console.log(stats);
    if(stats.failures === 0) {
        slackPost = 
            {
                icon_emoji: ":clap:",
                text: "all test passed. ",
                username: "e2e-bot"
            };
    } else {
        slackPost = 
            {
                icon_emoji: ":sos:",
                text: `test failed!! please see : ${s3BaseUrl}/mochawesome.html`,
                username: "e2e-bot"
            };
    }

    const res = await post(SLACK_WEBHOOK_URL, slackPost);
    console.log('Slack Posted...');
    console.log(res);

    context.done(null, 'Stack Destoried...');
};