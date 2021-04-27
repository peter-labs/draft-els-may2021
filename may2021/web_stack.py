from aws_cdk import (
  core,
  aws_cloudfront,
  aws_s3,
  aws_s3_deployment,
)

class WebsiteStack(core.Stack):

  def __init__(
    self,
    scope: core.Construct,
    id: str,
    # env: core.Environment,
    **kwargs,
    ) -> None:
    super().__init__(scope, id, **kwargs)

    # S3 bucket to store website static files (HTML, CSS, JS...)
    static_bucket = aws_s3.Bucket(
        self,
        'WebsiteStaticS3Bucket',
        # bucket_name='elsworkshop-website-static',
        removal_policy=core.RemovalPolicy.DESTROY,
        block_public_access=aws_s3.BlockPublicAccess.BLOCK_ALL
    )

    # CloudFront origin identity to associate with the S3 bucket
    origin = aws_cloudfront.OriginAccessIdentity(
        self,
        'elsworkshopS3OriginAccessIdentity',
        comment='Associated with serverless website static S3 bucket',
    )

    # create cloudfront
    self.cdn = aws_cloudfront.CloudFrontWebDistribution(
        self,
        'elsworkshopCDN',
        comment='CDN for a full-stack serverless website',
        origin_configs=[
            aws_cloudfront.SourceConfiguration(
                s3_origin_source=aws_cloudfront.S3OriginConfig(
                    s3_bucket_source=static_bucket,
                    origin_access_identity=origin,
                ),
                behaviors=[
                    aws_cloudfront.Behavior(
                        is_default_behavior=True,
                        min_ttl=core.Duration.hours(1),
                        max_ttl=core.Duration.hours(24),
                        default_ttl=core.Duration.hours(1),
                        compress=True,
                    )
                ],
            )
        ],
        default_root_object='index.html',
        enable_ip_v6=True,
        http_version=aws_cloudfront.HttpVersion.HTTP2,
        price_class=aws_cloudfront.PriceClass.PRICE_CLASS_100,
        viewer_protocol_policy=aws_cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,  
    )

    # deploy static site to S3
    aws_s3_deployment.BucketDeployment(
        self,
        'elsworkshopStaticS3Deployment',
        sources=[aws_s3_deployment.Source.asset('website_static')],
        destination_bucket=static_bucket,
        distribution=self.cdn,
    )