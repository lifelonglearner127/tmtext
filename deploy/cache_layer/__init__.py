# List of queues used for cache
CACHE_QUEUES_LIST = {
    'urgent': 'cache_sqs_ranking_spiders_tasks_urgent',
    'production': 'cache_sqs_ranking_spiders_tasks',
    'dev': 'cache_sqs_ranking_spiders_tasks_dev',
    'test': 'cache_sqs_ranking_spiders_tasks_tests'
}

# Location of remote amazon redis ElastiCache
REDIS_HOST = 'sqs-cache.4a6nml.0001.use1.cache.amazonaws.com'

REDIS_PORT = 6379

# Keys for sqs metrics in redis
INSTANCES_COUNTER_REDIS_KEY = 'daily_sqs_instances_counter'

TASKS_COUNTER_REDIS_KEY = 'executed_tasks_during_the_day'

HANDLED_TASKS_SORTED_SET = 'executed_tasks_sorted_set'
