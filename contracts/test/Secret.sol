pragma solidity ^0.5.4;

contract SecretRegistry {
    struct evidence {
        uint256 timestamp;
        uint256 endTime;
    }

    mapping(bytes32 => evidence) private secrethash_to_evidence;

    event SecretRevealed(bytes32 indexed secrethash, bytes32 secret, uint256 end_time);

    function registerSecret(bytes32 _secret, uint256 _endTime) public returns (bool) {
        bytes32 secrethash = sha256(abi.encodePacked(_secret));
        if (secrethash_to_evidence[secrethash].timestamp > 0) {
            return false;
        }
        secrethash_to_evidence[secrethash].timestamp = block.number;
        secrethash_to_evidence[secrethash].endTime = _endTime;
        emit SecretRevealed(secrethash, _secret, _endTime);
        return true;
    }

    function revealedBefore(bytes32 _secret, uint expiry) internal view returns(bool) {
	    uint256 t = secrethash_to_evidence[_secret].timestamp;
	    return (t > 0 && t <= expiry);
    }

    function getEndTime(bytes32 _secret) internal view returns(uint256) {
	    return secrethash_to_evidence[_secret].endTime;
    }
}