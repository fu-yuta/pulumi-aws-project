import pulumi
import pulumi_aws as aws

# VPCの作成
vpc = aws.ec2.Vpc(
    "pulumi-vpc",
    cidr_block="10.0.0.0/16",
    tags={
        "Name": "pulumi-vpc",
    })

# Subnetの作成
public_subnet_a = aws.ec2.Subnet(
    "pulumi-public-subnet-a",
    cidr_block="10.0.1.0/24",
    availability_zone="ap-northeast-1a",
    tags={
        "Name": "pulumi-public-subnet-a",
    },
    vpc_id=vpc.id)

public_subnet_c = aws.ec2.Subnet(
    "pulumi-public-subnet-c",
    cidr_block="10.0.2.0/24",
    availability_zone="ap-northeast-1c",
    tags={
        "Name": "pulumi-public-subnet-c",
    },
    vpc_id=vpc.id)

private_subnet_a = aws.ec2.Subnet(
    "pulumi-private-subnet-a",
    cidr_block="10.0.3.0/24",
    availability_zone="ap-northeast-1a",
    tags={
        "Name": "pulumi-private-subnet-a",
    },
    vpc_id=vpc.id)

private_subnet_c = aws.ec2.Subnet(
    "pulumi-private-subnet-c",
    cidr_block="10.0.4.0/24",
    availability_zone="ap-northeast-1c",
    tags={
        "Name": "pulumi-private-subnet-c",
    },
    vpc_id=vpc.id)

# InternetGatewayの作成
igw = aws.ec2.InternetGateway(
    "pulumi-igw",
    tags={
        "Name": "pulumi-igw",
    },
    vpc_id=vpc.id)

# EIPの作成
ngw_eip_a = aws.ec2.Eip("pulumi-ngw-eip-a")

ngw_eip_c = aws.ec2.Eip("pulumi-ngw-eip-c")

# NatGatewayの作成
ngw_a = aws.ec2.NatGateway(
    "pulumi-ngw-a",
    allocation_id=ngw_eip_a.id,
    subnet_id=public_subnet_a.id)

# NatGatewayの作成
ngw_c = aws.ec2.NatGateway(
    "pulumi-ngw-c",
    allocation_id=ngw_eip_c.id,
    subnet_id=public_subnet_c.id)

# RouteTableの作成
public_route_table_a = aws.ec2.RouteTable(
    "pulumi-public-route-table-a",
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "gateway_id": igw.id,
        },
    ],
    tags={
        "Name": "pulumi-public-route-table-a",
    },
    vpc_id=vpc.id)

public_route_table_c = aws.ec2.RouteTable(
    "pulumi-public-route-table-c",
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "gateway_id": igw.id,
        },
    ],
    tags={
        "Name": "pulumi-public-route-table-c",
    },
    vpc_id=vpc.id)

private_route_table_a = aws.ec2.RouteTable(
    "pulumi-private-route-table-a",
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "nat_gateway_id": ngw_a.id,
        },
    ],
    tags={
        "Name": "pulumi-private-route-table-a",
    },
    vpc_id=vpc.id)

private_route_table_c = aws.ec2.RouteTable(
    "pulumi-private-route-table-c",
    routes=[
        {
            "cidr_block": "0.0.0.0/0",
            "nat_gateway_id": ngw_c.id,
        },
    ],
    tags={
        "Name": "pulumi-private-route-table-c",
    },
    vpc_id=vpc.id)

# RouteTableAssociationの作成
route_table_association_public_a = aws.ec2.RouteTableAssociation(
    "pulumi-route-table-association-public-a",
    subnet_id=public_subnet_a.id,
    route_table_id=public_route_table_a.id)

route_table_association_public_c = aws.ec2.RouteTableAssociation(
    "pulumi-route-table-association-public-c",
    subnet_id=public_subnet_c.id,
    route_table_id=public_route_table_c.id)

route_table_association_private_a = aws.ec2.RouteTableAssociation(
    "pulumi-route-table-association-private-a",
    subnet_id=private_subnet_a.id,
    route_table_id=private_route_table_a.id)

route_table_association_private_c = aws.ec2.RouteTableAssociation(
    "pulumi-route-table-association-private-c",
    subnet_id=private_subnet_c.id,
    route_table_id=private_route_table_c.id)

# SecurityGroupの作成
alb_sg = aws.ec2.SecurityGroup(
    "pulumi-alb-sg",
    ingress=[
        {
            "from_port": 80,
            "protocol": "TCP",
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"]
        },
    ],
    egress=[
        {
            "from_port": 0,
            "protocol": "TCP",
            "to_port": 65535,
            "cidr_blocks": ["0.0.0.0/0"]
        },
    ],
    tags={
        "Name": "pulumi-alb-sg",
    },
    vpc_id=vpc.id)

ec2_sg = aws.ec2.SecurityGroup(
    "pulumi-ec2-sg",
    ingress=[
        {
            "from_port": 80,
            "protocol": "TCP",
            "to_port": 80,
            "security_groups": [alb_sg.id]
        },
        {
            "from_port": 22,
            "protocol": "TCP",
            "to_port": 22,
            "cidr_blocks": ["0.0.0.0/0"]
        },
    ],
    egress=[
        {
            "from_port": 0,
            "protocol": "TCP",
            "to_port": 65535,
            "cidr_blocks": ["0.0.0.0/0"]
        },
    ],
    tags={
        "Name": "pulumi-ec2-sg",
    },
    vpc_id=vpc.id)

rds_sg = aws.ec2.SecurityGroup(
    "pulumi-rds-sg",
    ingress=[
        {
            "from_port": 3306,
            "protocol": "TCP",
            "to_port": 3306,
            "security_groups": [ec2_sg.id]
        },
    ],
    egress=[
        {
            "from_port": 0,
            "protocol": "TCP",
            "to_port": 65535,
            "cidr_blocks": ["0.0.0.0/0"]
        },
    ],
    tags={
        "Name": "pulumi-rds-sg",
    },
    vpc_id=vpc.id)

# KeyPairの作成
key_pair = aws.ec2.KeyPair(
    "pulumi-keypair",
    public_key="",
    tags={
        "Name": "pulumi-keypair",
    })

#  TargetGroupの作成
target_group = aws.alb.TargetGroup(
    "pulumi-target-group",
    health_check={
        "healthyThreshold": 5,
        "interval": 30,
        "matcher": "200,302",
        "path": "/",
        "protocol": "HTTP",
        "timeout": 5,
        "unhealthyThreshold": 2
    },
    name="pulumi-target-group",
    port=80,
    protocol="HTTP",
    tags={
        "Name": "pulumi-target-group",
    },
    target_type="instance",
    vpc_id=vpc.id)

# ユーザデータの読み込み
file = open("./user-data")
user_data = file.read()

# LaunchConfigurationの作成
launch_conf = aws.ec2.LaunchConfiguration(
    "pulumi-launch-conf",
    image_id="ami-0ee1410f0644c1cac",
    instance_type="t2.micro",
    associate_public_ip_address=True,
    key_name=key_pair.key_name,
    security_groups=[ec2_sg.id],
    user_data=user_data)

file.close()

# AutoScalingGroupの作成
autoscaling_group = aws.autoscaling.Group(
    "pulumi-autoscaling-group",
    availability_zones=["ap-northeast-1a", "ap-northeast-1c"],
    health_check_type="ELB",
    desired_capacity=1,
    launch_configuration=launch_conf.name,
    max_size=1,
    min_size=1,
    target_group_arns=[target_group.arn],
    vpc_zone_identifiers=[
        private_subnet_a.id,
        private_subnet_c.id
    ])

# LoadBalancerの作成
alb = aws.alb.LoadBalancer(
    "pulumi-alb",
    load_balancer_type="application",
    name="pulumi-alb",
    security_groups=[alb_sg.id],
    subnets=[
        public_subnet_a.id,
        public_subnet_c.id
    ],
    tags={
        "Name": "pulumi-alb",
    })

# Listenerの作成
alb_listener = aws.alb.Listener(
    "pulumi-alb-listener",
    default_actions=[{
        "target_group_arn": target_group.arn,
        "type": "forward",
    }],
    load_balancer_arn=alb.arn,
    port="80",
    protocol="HTTP")

# RDS SubnetGroupの作成
rds_subnet = aws.rds.SubnetGroup(
    "pulumi-rds-subnet",
    subnet_ids=[
        private_subnet_a.id,
        private_subnet_c.id,
    ],
    tags={
        "Name": "pulumi-rds-subnet",
    })

#RDSインスタンスの作成
rds = aws.rds.Instance(
    "pulumi-rds",
    allocated_storage=20,
    db_subnet_group_name=rds_subnet.name,
    engine="mysql",
    engine_version="5.7",
    identifier="pulumi-rds",
    instance_class="db.t2.micro",
    name="pulumi",
    parameter_group_name="default.mysql5.7",
    password="password",
    skip_final_snapshot=True,
    storage_type="gp2",
    tags={
        "Name": "pulumi-rds",
    },
    username="admin",
    vpc_security_group_ids=[rds_sg.id])