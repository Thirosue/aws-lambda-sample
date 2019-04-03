const INSTANCE_ID = 'i-0ea5ddbc554991927';
const sleep = msec => new Promise(resolve => setTimeout(resolve, msec));

const AWS = require('aws-sdk'); 
AWS.config.region = 'us-east-1';

const ec2 = new AWS.EC2();

// EC2 Run Commandの実行ターゲット
const target_instance_ids = [INSTANCE_ID];

// 実行コマンド
const cmd = 
`echo test`;
const ec2_run_command = `/sbin/runuser -l ec2-user -c \'${cmd}\'`;

exports.handler = async (context) => {
    //----------------  Wait EC2 Enable
    const ec2Params = {
        InstanceIds: [
            INSTANCE_ID
        ]
    };
  
    let state = 'disabled';
    do {
        var { Reservations } = await ec2.describeInstances(ec2Params).promise();
        var target = Reservations[0].Instances[0];
        state = target.State.Name;
        console.log(state);  
        await sleep(3000); //wait 3s
    } while (!['running'].includes(state));

    //----------------  Exec Command
    const ssm = new AWS.SSM();
    const ssm_send_command_params = {
        DocumentName: 'AWS-RunShellScript',
        InstanceIds: target_instance_ids,
        Parameters: {
            'commands': [
                ec2_run_command,
            ],
        },
        TimeoutSeconds: 3600    // 1 hour
    };
    const data = await ssm.sendCommand(ssm_send_command_params).promise();
    console.log(data);           // successful response

    const response = {
        statusCode: 200,
        body: JSON.stringify('Hello from Lambda!'),
    };
    return response;
};
