# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import time

from heracles.hive.hive_metastore import ttypes


class HiveMappers:
    @staticmethod
    def map_glue_database(glue_database):
        return ttypes.Database(
            name=glue_database.get('Name'),
            description=glue_database.get('Description', ""),
            locationUri=glue_database.get('LocationUri', ""),
            parameters=glue_database.get('Parameters', {})
        )

    @staticmethod
    def map_glue_table(databaseName, tableName, glue_table):
        # Create the base table type
        table = ttypes.Table(
            tableName=tableName,
            dbName=databaseName,
            owner=glue_table.get('Owner', None),
            createTime=0,
            lastAccessTime=HiveMappers.unix_epoch_as_int(glue_table.get('LastAccessTime', None)),
            retention=glue_table.get('Retention', None),
            tableType=glue_table.get('TableType'),
            parameters=glue_table.get('Parameters', {}),
            viewOriginalText=None,
            viewExpandedText=None,
            partitionKeys=[
                ttypes.FieldSchema(
                    name=key['Name'],
                    type=key['Type']
                ) for key in glue_table.get('PartitionKeys', [])
            ]
        )
        # Map the storage description
        sd = ttypes.StorageDescriptor(
            cols=[
                ttypes.FieldSchema(
                    name=rec['Name'],
                    type=rec['Type']
                ) for rec in glue_table['StorageDescriptor']['Columns']
            ],
            location=glue_table['StorageDescriptor'].get('Location'),
            inputFormat=glue_table['StorageDescriptor'].get('InputFormat'),
            outputFormat=glue_table['StorageDescriptor'].get('OutputFormat'),
            compressed=glue_table['StorageDescriptor'].get('Compressed'),
            numBuckets=glue_table['StorageDescriptor'].get('NumberOfBuckets', -1),
            serdeInfo=ttypes.SerDeInfo(
                serializationLib=glue_table['StorageDescriptor']['SerdeInfo']['SerializationLibrary'],
                parameters=glue_table['StorageDescriptor']['SerdeInfo']['Parameters'],
            ),
            bucketCols=glue_table['StorageDescriptor'].get('BucketColumns', []),
            sortCols=glue_table['StorageDescriptor'].get('SortColumns', []),
            parameters=glue_table['StorageDescriptor'].get('Parameters', {}),
            skewedInfo=ttypes.SkewedInfo(
                skewedColNames=glue_table['StorageDescriptor'].get('SkewedInfo', {}).get('SkewedColumnNames', []),
                skewedColValues=glue_table['StorageDescriptor'].get('SkewedInfo', {}).get('SkewedColumnValues', []),
                skewedColValueLocationMaps=(
                    glue_table['StorageDescriptor']
                    .get('SkewedInfo', {})
                    .get('SkewedColumnValueLocationMaps', {})
                ),
            ),
            storedAsSubDirectories=glue_table['StorageDescriptor'].get('StoredAsSubDirectories'),
        )
        table.sd = sd

        return table

    @staticmethod
    def map_glue_partition_for_table(databaseName, tableName, glue_partition):
        hive_partition = ttypes.Partition(
            values=glue_partition.get('Values'),
            dbName=databaseName,
            tableName=tableName,
            createTime=HiveMappers.unix_epoch_as_int(glue_partition.get('CreationTime', None)),
            lastAccessTime=HiveMappers.unix_epoch_as_int(glue_partition.get('LastAccessTime', None)),
            parameters=glue_partition.get('Parameters', {})
        )
        sd = ttypes.StorageDescriptor(
            cols=[
                ttypes.FieldSchema(
                    name=rec['Name'],
                    type=rec['Type']
                ) for rec in glue_partition['StorageDescriptor']['Columns']
            ],
            location=glue_partition['StorageDescriptor'].get('Location'),
            inputFormat=glue_partition['StorageDescriptor'].get('InputFormat'),
            outputFormat=glue_partition['StorageDescriptor'].get('OutputFormat'),
            compressed=glue_partition['StorageDescriptor'].get('Compressed'),
            numBuckets=glue_partition['StorageDescriptor'].get('NumberOfBuckets', -1),
            serdeInfo=ttypes.SerDeInfo(
                serializationLib=glue_partition['StorageDescriptor']['SerdeInfo']['SerializationLibrary'],
                parameters=glue_partition['StorageDescriptor']['SerdeInfo']['Parameters'],
            ),
            bucketCols=glue_partition['StorageDescriptor'].get('BucketColumns', []),
            sortCols=glue_partition['StorageDescriptor'].get('SortColumns', []),
            parameters=glue_partition['StorageDescriptor'].get('Parameters', {}),
            skewedInfo=ttypes.SkewedInfo(
                skewedColNames=glue_partition['StorageDescriptor'].get('SkewedInfo', {}).get('SkewedColumnNames', []),
                skewedColValues=glue_partition['StorageDescriptor'].get('SkewedInfo', {}).get('SkewedColumnValues', []),
                skewedColValueLocationMaps=(
                    glue_partition['StorageDescriptor']
                    .get('SkewedInfo', {})
                    .get('SkewedColumnValueLocationMaps', {})
                ),
            ),
            storedAsSubDirectories=glue_partition['StorageDescriptor'].get('StoredAsSubDirectories'),
        )
        hive_partition.sd = sd

        return hive_partition

    @staticmethod
    def unix_epoch_as_int(datetime_obj):
        if datetime_obj is not None:
            return int(time.mktime(datetime_obj.timetuple()))
        else:
            return 0
