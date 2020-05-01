'use strict';

console.log("loading...")

const aws = require('aws-sdk');
const s3 = new aws.S3({
  apiVersion: '2006-03-01'
});
const node_zip = require('node-zip');
const mime = require('mime-types');
const axios = require('axios');

const yubinURL = process.env.ZIPCODE_DL_URL;
const Bucket = `${process.env.ZIPCODE_BUCKET}/target`;

const header = {
  responseType: 'arraybuffer',
  headers: {
    Accept: 'application/zip'
  }
}

const lookup_mime = async (name) => {
  const mimetype = mime.lookup(name) || 'application/octet-stream';
  console.log(name, mimetype);
  return mimetype;
}

exports.handler = async (event, context) => {
  console.log('Received event:', JSON.stringify(event, null, 2));

  let Body;
  let ContentType;
  await axios.get(yubinURL, header)
    .then(async response => {
      Body = response.data;
      ContentType = response.headers['content-type']
    })
    .catch(async error => {
      console.error(error);
    });

  try {
    console.log('CONTENT TYPE:', ContentType);
    const zip = new node_zip(Body, {
      base64: false,
      checkCRC32: true
    })
    var dt = new Date();
    const dir = `${dt.getFullYear()}${("00" + (dt.getMonth()+1)).slice(-2)}${("00" + dt.getDate()).slice(-2)}_`; //yyyymmdd
    const i = Object.keys(zip.files).shift();
    const f = zip.files[i];
    const putParams = {
      Bucket,
      Key: `${dir}${f.name}`,
      Body: new Buffer.from(f.asBinary(), 'binary'),
      ContentType: await lookup_mime(f.name),
      // ACL: 'public-read'
    };

    console.log("putParams", putParams)
    await s3.putObject(putParams).promise().then((data) => {
      console.log("download and unzip Success!!", data);
      context.done(); // 正常終了
    }).catch(err => {
      console.error(err)
    })

  } catch (err) {
    console.log(err);
  }
};