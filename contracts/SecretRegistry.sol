pragma solidity ^0.5.4;
import "./ECVerify.sol";

contract SecretRegistry {

    struct evidence {
        uint256 reveal_time;
        uint256 endTime;
    }
    mapping(bytes32 => evidence) private secrethash_to_evidence;

    event SecretRevealed(bytes32 indexed secrethash, bytes32 secret, uint256 endTime);

    function registerSecret(bytes32 secret, address target, uint256 endTime, bytes memory signature) public returns (bool) {
        bytes32 secrethash = keccak256(abi.encodePacked(secret));
        secrethash = keccak256(abi.encodePacked(secrethash, target));   // Only the endTime with the sign of the target must be entered to be valid.
        bytes32 endTimehash =  keccak256(abi.encodePacked(endTime));
        address signature_address = ECVerify.ecverify(endTimehash, signature);

        if (secret == bytes32(0x0) || secrethash_to_evidence[secrethash].reveal_time > 0 || signature_address != target) {
            return false;
        }
        // case -> target regist secret
        if (target == msg.sender) {
            endTime = 0;
        }
        secrethash_to_evidence[secrethash].reveal_time = block.number;
        secrethash_to_evidence[secrethash].endTime = endTime;
        emit SecretRevealed(secrethash, secret, endTime);
        return true;
    }

    function setEndTime(bytes32 secrethash, address target, uint256 endTime) public returns(uint256){
        secrethash = keccak256(abi.encodePacked(secrethash, target));

        secrethash_to_evidence[secrethash].endTime = endTime;
        return endTime;
    }

    function getSecretRevealTime(bytes32 secrethash, address target) public view returns (uint256) {
        secrethash = keccak256(abi.encodePacked(secrethash, target));

        return secrethash_to_evidence[secrethash].reveal_time;
    }

    function getEndtime(bytes32 secrethash, address target) public view returns (uint256) {
        secrethash = keccak256(abi.encodePacked(secrethash, target));

        return secrethash_to_evidence[secrethash].endTime;
    }
}