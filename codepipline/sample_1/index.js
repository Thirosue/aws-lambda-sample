'use strict';

const node_zip = require('node-zip');

const aws = require('aws-sdk');
const s3 = new aws.S3({ apiVersion: '2006-03-01' });
const codebuild = new aws.CodeBuild({apiVersion: '2016-10-06'});
const codepipeline = new aws.CodePipeline({apiVersion: '2015-07-09'});

const sleep = msec => new Promise(resolve => setTimeout(resolve, msec));

const src_bucket = 'codepipeline-us-east-1-12981354025';
const src_prefix = 'vue-sample-e2e/Provision/';
const dest_bucket = 'vue-sample-terraform-state';

const listParams = {
  Bucket: src_bucket,
  Prefix: src_prefix,
};

exports.handler = async (event, context) => {
  let jobId;
  
  try {
    const jobEvent = event['CodePipeline.job'];
    const jobId = jobEvent ? jobEvent.id : null;

    const { Contents } = await s3.listObjects(listParams).promise();
    const currentBuildObject = Contents.sort((a,b)=>(a.LastModified - b.LastModified)).pop();
    console.log('currentBuildObject:', currentBuildObject);
    const getParams = {
        Bucket: src_bucket,
        Key: currentBuildObject.Key,
    };
    
    const data = await s3.getObject(getParams).promise();
    const zip = new node_zip(data.Body, {base64: false, checkCRC32: true});
  
    const promises = 
      Object.keys(zip.files).map(i => {
        const f = zip.files[i];
        console.log(`${f.name} putting ...`);
        const putObject = 
                {
                    Bucket: dest_bucket,
                    Key   : f.name,
                    Body  : new Buffer(f.asBinary(), 'binary')
                };    
        return s3.putObject(putObject).promise();
      });
  
    console.log(`target Promises`);
    console.log(promises);
  
    await Promise.all(promises)
      .then(results => {
        console.log(results);
      });
    
    console.log('Waiting S3 Sync ...');
    await sleep("60000");
      
    console.log('Destroy Start !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!');
      
    const buildParams = {
      projectName: 'vue-sample-destroy-for-e2e'
    };
        
    await codebuild.startBuild(buildParams).promise();
    const params = {
      jobId
    };
    await codepipeline.putJobSuccessResult(params).promise();

    console.log('End...')
  } catch (err) {
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