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

exports.handler = async (event, context) => {
    const options = 
    {
        text: "test",
        username: "slackbot",
        channel: "#random"
    };

    const res = await post(SLACK_WEBHOOK_URL, options);
    console.log('Slack Posted...');
    console.log(res);
};