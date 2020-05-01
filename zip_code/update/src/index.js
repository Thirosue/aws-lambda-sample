const AWS = require('aws-sdk');
const mysql = require('promise-mysql');
const iconv = require('iconv-lite');
const parse = require('csv-parse');

const s3 = new AWS.S3();
const ssm = new AWS.SSM();

let pool = null;

exports.handler = async (event, context) => {
  const host = await getSSMData(process.env.DATABASE_HOST, true);
  const password = await getSSMData(process.env.DATABASE_PASSWORD, true);

  // RDS情報
  pool = await mysql.createConnection({
    host,
    port: 3306,
    database: 'db',
    user: 'root',
    password,
  });
  console.log('コネクションを接続します');

  // サーバがコネクションを切った場合は再接続
  pool.on('error', async (err) => {
    if (err.code === 'PROTOCOL_CONNECTION_LOST') {
      pool = await mysql.createConnection({
        host,
        port: 3306,
        database: 'db',
        user: 'root',
        password,
      });
      console.log(`Reconnected`);
    } else {
      throw err;
    }
  });

  try {
    // read csv
    const targetLines = await getCsvLines(process.env.ZIPCODE_BUCKET, 'target/KEN_ALL.CSV');

    // トランザクションを開始
    await pool.beginTransaction();
    console.log("start insert ....");

    pool.query('DELETE FROM zip_code'); // delete
    const now = new Date();
    const values = targetLines.map(line=>[line[2],line[6],line[7],line[8],now]);
    console.log(values);

    // insert
    const promises = 
      values.map(value => {
        return pool.query('INSERT INTO zip_code VALUES (?,?,?,?,?)', value);
      });

    await Promise.all(promises)
      .then(results => {
        console.log(results);
      });

    // コミット
    await pool.commit();
    console.log("end insert ....");
    context.done();

  } catch (e) {
    // 異常終了によりロールバックし、コネクション破棄
    console.log(e);
    pool.rollback();

  } finally {
    // コネクション破棄
    console.log('コネクションを破棄します');
    pool.end();    
  }
};

// SSM Parameterから値を取得
const getSSMData = async (key, isSecret) => {
  const value = await ssm
    .getParameter({
      Name: key,
      WithDecryption: isSecret,
    })
    .promise();

  return value.Parameter.Value;
};

// 格納されたcsvファイルの行を取得する
const getCsvLines = async (srcBucket, srcKey) => {
  return new Promise(async resolve => {
    const params = {
      Bucket: srcBucket,
      Key: srcKey,
    };

    const parser = parse({
      delimiter: ','
    });
  
    // S3からcsvデータをstreamingで取得
    await s3.getObject(params).createReadStream()
      .pipe(iconv.decodeStream('Shift_JIS'))
      .pipe(iconv.encodeStream('UTF-8'))
      .pipe(parser);

    const output = [];
      
    parser.on('readable', () => {
      let record;
      while (record = parser.read()) {
        output.push(record);
      }
    });

    parser.on('error', (err) => {
      console.error(err.message);
    });

    parser.on('end', () => {
      resolve(output);
    });
  });
};