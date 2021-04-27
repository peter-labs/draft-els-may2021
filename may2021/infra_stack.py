from aws_cdk import (
    core,
    aws_s3,
    aws_lambda,
    aws_apigateway,
    aws_iam
)



class InfraStack(core.Stack):

  def __init__(
    self,
    scope: core.Construct,
    id: str,
    # env: core.Environment,
    **kwargs,
    ) -> None:
      super().__init__(scope, id, **kwargs)

      bucket = aws_s3.Bucket(self, 
          "S3Upload", 
          versioned=True,)

      lambda_upload = aws_lambda.Function(
          self, 'LambdaUpload',
          runtime=aws_lambda.Runtime.PYTHON_3_8,
          code=aws_lambda.Code.asset('lambda'),
          handler='upload.handler',
      )
      lambda_upload.add_to_role_policy(
        aws_iam.PolicyStatement(
          actions=["s3:PutObject"],
          resources=[
              "{}/*".format(bucket.bucket_arn)
          ]
        )
      )

      lambda_listimages = aws_lambda.Function(
          self, 'LambdaListImages',
          runtime=aws_lambda.Runtime.PYTHON_3_8,
          code=aws_lambda.Code.asset('lambda'),
          handler='listimages.handler',
      )

      # create REST API
      api = aws_apigateway.RestApi(self, 'RestAPI',
        rest_api_name='ELS API')

      # adding a method to list images
      list_images_resources = api.root.add_resource("list")
      list_images_integration = aws_apigateway.LambdaIntegration(lambda_listimages, proxy=True)
      list_images_method = list_images_resources.add_method(
          "GET",
          list_images_integration,
          api_key_required=False
      )

      # adding a method to initiate image upload
      upload_image_resources = api.root.add_resource("upload")
      upload_image_integration = aws_apigateway.LambdaIntegration(lambda_upload, proxy=True)
      upload_image_method = upload_image_resources.add_method(
          "POST",
          upload_image_integration,
          api_key_required=False
      )





