<?php
require_once FCPATH.'application/libraries/vendor/autoload.php';
use Aws\Common\Aws;
use Aws\Common\Enum\Region;
use Aws\Ec2\Ec2Client;
use Aws\Ec2\Ec2Exception;

class Awslib {
    private $aws;
    private $ec2client;
    private $CI;

    public $debug=true;
    public $ssh=true;
    public $securityGroupName = 'test-security-group';

    public $errors = array();

    function __construct(){
        $this->CI =& get_instance();
        $this->aws = Aws::factory(array(
        	'key'    => $this->CI->config->item('aws_access_key_id'),
        	'secret' => $this->CI->config->item('aws_secret_key'),
        	'region' => $this->CI->config->item('aws_region')
        ));

        $this->ec2client = $this->aws->get('ec2');
    }

    function security() {
		try {
			$result = $this->ec2client->describeSecurityGroups(array(
			    'GroupNames' => array($this->securityGroupName)
			));
		} catch(Exception $e) {
			if ($e->getExceptionCode() == 'InvalidGroup.NotFound') {
				//Creating group
				$result = $this->ec2client->createSecurityGroup(array(
				    'GroupName'   => $this->securityGroupName,
				    'Description' => 'ssh server security'
				));

				if ($this->ssh) {
					// SSH auth
					$this->ec2client->authorizeSecurityGroupIngress(array(
					    'GroupName'     => $this->securityGroupName,
					    'IpPermissions' => array(
					        array(
					            'IpProtocol' => 'tcp',
					            'FromPort'   => 22,
					            'ToPort'     => 22,
					            'IpRanges'   => array(
					                array('CidrIp' => '0.0.0.0/0')
					            ),
					        )
					    )
					));
				}
			} else {
				if ($this->debug) {
					$this->errors[] = $e->getMessage();
				}
				return false;
			}
		}

		return true;
    }

    function run($min=1,$max=1) {
    	if (!$this->security()) {
    		return false;
    	}

		$result = $this->ec2client->runInstances(array(
		    'ImageId'        => $this->CI->config->item('aws_ami_id'),
		    'MinCount'       => $min,
		    'MaxCount'       => $max,
		    'InstanceType'   => $this->CI->config->item('aws_instance_type'),
//		    'KeyName'        => $keyPairName,
		    'SecurityGroups' => array($this->securityGroupName),
		));

		return $result;
    }

	function runSpot($price='0.005', $count=1) {
    	if (!$this->security()) {
    		return false;
    	}

		$result = $this->ec2client->requestSpotInstances(array(
    		'SpotPrice' => $price,
			'InstanceCount' => $count,
			'LaunchSpecification' => array(
				'ImageId' => $this->CI->config->item('aws_ami_id'),
				'InstanceType' => $this->CI->config->item('aws_instance_type'),
				'SecurityGroups' => array($this->securityGroupName),
			),
		));

		return $result;
    }

    function stop($ids){
		$result = $this->ec2client->stopInstances(array(
		    'InstanceIds' => $ids,
		    'Force' => true
		));
		return $result;
    }

    function terminate($ids){
		$result = $this->ec2client->terminateInstances(array(
		    'InstanceIds' => $ids
		));
		return $result;
    }

    function status() {
		$result = $this->ec2client->describeInstanceStatus();
		return $result;
    }

    function describe($ids) {
    	$result = $this->ec2client->describeInstances(array(
		    'InstanceIds' => $ids,
		));
		return $result;
    }

    function describeSpot($ids) {
    	$result = $this->ec2client->describeSpotInstanceRequests(array(
		    'SpotInstanceRequestIds' => $ids,
		));
		return $result;
    }

    function waitRunning($ids) {
    	$this->ec2client->waitUntilInstanceRunning(array(
		    'InstanceIds' => $ids,
		));
    }

    function waitTerminated($ids) {
    	$this->ec2client->waitUntilInstanceTerminated(array(
		    'InstanceIds' => $ids,
		));
    }

    function cancelSpot($ids) {
    	$result = $this->ec2client->cancelSpotInstanceRequests(array(
		    'SpotInstanceRequestIds' => $ids,
		));
		return $result;
    }

}
?>