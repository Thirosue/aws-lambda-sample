let mysql = require('mysql');

let connection;
  
connection = mysql.createConnection({
  host   : process.env['endpoint'], // use db proxy endpoint
  user   : process.env['user'],
  password : process.env['password'],
  database : process.env['db']
});

const query = (connection, statement) => {
  return new Promise((resolve, reject) => {
    connection.query(statement, (err, results, fields) => {
      if (err) {
        reject(err);
      } else {
        resolve(results, fields);
      }
    });
  });
};

exports.handler = async (event, context) => {
    const sql ="SELECT * FROM information_schema.PROCESSLIST";

    const res = await query(connection, sql);
    console.log(JSON.stringify(res));

    connection.end();
};