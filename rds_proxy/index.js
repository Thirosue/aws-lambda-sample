// @see https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-database.html
// @see https://aws.amazon.com/jp/blogs/compute/using-amazon-rds-proxy-with-aws-lambda/
let AWS = require('aws-sdk');
const mysql2 = require('mysql2/promise');

let connection;
const username = 'admin'; // set your username

exports.handler = async(event) => {
	console.log("Starting query ...\n");
	console.log("Running iam auth ...\n");

	const signer = new AWS.RDS.Signer({
	    region: 'ap-northeast-1',
	    hostname: process.env['proxy_endpoint'], // set your rds proxy endpoint
	    port: 3306,
	    username
	});

	const token = signer.getAuthToken({
	  username
	});
	console.log(token);
	console.log ("IAM Token obtained\n");
	
	const connectionConfig = {
	  host: process.env['proxy_endpoint'], // set your rds proxy endpoint
	  user: username,
	  database: 'mysql', // set your database name
	  ssl: 'Amazon RDS',
	  password: token,
	  authPlugins: { mysql_clear_password: () => () => signer.getAuthToken() }
	};

	connection = await mysql2.createConnection(connectionConfig);	
	const [rows, fields] = await connection.query("SELECT 1");
	console.log(rows);
};