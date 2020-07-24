
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

# RouteTableAssociationの作成
route_table_association_public_a = aws.ec2.RouteTableAssociation(
    "pulumi-route-table-association-public-a",
    subnet_id=public_subnet_a.id,
    route_table_id=public_route_table_a.id)

route_table_association_public_c = aws.ec2.RouteTableAssociation(
    "pulumi-route-table-association-public-c",
    subnet_id=public_subnet_c.id,
    route_table_id=public_route_table_c.id)

# SecurityGroupの作成
ec2_sg = aws.ec2.SecurityGroup(
    "pulumi-ec2-sg",
    ingress=[
        {
            "from_port": 80,
            "protocol": "TCP",
            "to_port": 80,
            "cidr_blocks": ["0.0.0.0/0"]
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

# EC2インスタンスの作成
ec2 = aws.ec2.Instance(
    "pulumi-ec2",
    ami="ami-0ee1410f0644c1cac",
    instance_type="t2.micro",
    subnet_id=public_subnet_a.id,
    tags={
        "Name": "pulumi-ec2",
    },
    associate_public_ip_address=True,
    key_name=key_pair.key_name,
    user_data="#!/bin/bash \n\n yum install -y mysql",
    vpc_security_group_ids=[ec2_sg.id])

# EIPの作成
ec2_eip = aws.ec2.Eip(
    "pulumi-eip-ec2",
    instance=ec2.id,
    tags={
        "Name": "pulumi-eip-ec2",
    },
    vpc=True)

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
