pragma solidity ^0.5.4;
import "./SecretRegistry.sol";

contract channel {
    // Token public token;
    // uint256 public chain_id;
    // uint256 constant public MAX_SAFE_UINT256 = (
    //     115792089237316195423570985008687907853269984665640564039457584007913129639935
    // );
    // address public deprecation_executor;
    // bool public safety_deprecation_switch = false;

    SecretRegistry public secret_registry;

    string public constant signature_prefix = '\x19Ethereum Signed Message:\n';

    uint256 public channel_participant_deposit_limit;
    uint256 public token_network_deposit_limit;

    uint256 public settlement_timeout_min;
    uint256 public settlement_timeout_max;
    uint256 public channel_counter;

    mapping (uint256 => Channel) public channels;

    mapping (bytes32 => uint256) public participants_hash_to_channel_identifier;

    mapping(bytes32 => UnlockData) private unlock_identifier_to_unlock_data;

    struct Participant {
        uint256 deposit;
        uint256 withdrawn_amount;
        bool is_the_closer;
        bytes32 balance_hash;
        uint256 nonce;
    }

    enum ChannelState {
        NonExistent, // 0
        Opened,      // 1
        Closed,      // 2
        Settled,     // 3; Note: The channel has at least one pending unlock
        Removed      // 4; Note: Channel data is removed, there are no pending unlocks
    }

    struct Channel {
        uint256 settle_block_number;

        ChannelState state;

        mapping(address => Participant) participants;
    }

    struct SettlementData {
        uint256 deposit;
        uint256 withdrawn;
        uint256 transferred;
        uint256 locked;
    }

    struct UnlockData {
        bytes32 locksroot;
        uint256 locked_amount;
    }

    event ChannelNewDeposit(
        uint256 indexed channel_identifier,
        address indexed participant,
        uint256 total_deposit
    );

    event ChannelOpened(
        uint256 indexed channel_identifier,
        address indexed participant1,
        address indexed participant2,
        uint256 settle_timeout
    );

    modifier isOpen(uint256 channel_identifier) {
        require(channels[channel_identifier].state == ChannelState.Opened);
        _;
    }

    modifier settleTimeoutValid(uint256 timeout) {
        require(timeout >= settlement_timeout_min);
        require(timeout <= settlement_timeout_max);
        _;
    }
    constructor(
        // address _token_address,
         address _secret_registry
        // uint256 _chain_id,
//        uint256 _settlement_timeout_min,
//        uint256 _settlement_timeout_max,
//        uint256 _channel_participant_deposit_limit,
//        uint256 _token_network_deposit_limit
    )
        public
    {
        // require(_token_address != address(0x0));
         require(_secret_registry != address(0x0));
        // require(_deprecation_executor != address(0x0));
        // require(_chain_id > 0);
//        require(_settlement_timeout_min > 0);
//        require(_settlement_timeout_max > _settlement_timeout_min);
//        require(_channel_participant_deposit_limit > 0);
//        require(_token_network_deposit_limit > 0);
//        require(_token_network_deposit_limit >= _channel_participant_deposit_limit);

        // token = Token(_token_address);
         secret_registry = SecretRegistry(_secret_registry);
        // chain_id = _chain_id;
        // require(token.totalSupply() > 0);
        // deprecation_executor = _deprecation_executor;

//        settlement_timeout_min = _settlement_timeout_min;
//        settlement_timeout_max = _settlement_timeout_max;
//        channel_participant_deposit_limit = _channel_participant_deposit_limit;
//        token_network_deposit_limit = _token_network_deposit_limit;
    }

    // function deprecate() public isSafe onlyDeprecationExecutor {
    //     safety_deprecation_switch = true;
    //     emit DeprecationSwitch(safety_deprecation_switch);
    // }

    function openChannel(address participant1, address participant2, uint256 settle_timeout)
        public
        // isSafe
//        settleTimeoutValid(settle_timeout)
        returns (uint256)
    {
        bytes32 pair_hash;
        uint256 channel_identifier;

        // require(token.balanceOf(address(this)) < token_network_deposit_limit);

        channel_counter += 1;
        channel_identifier = channel_counter;

        pair_hash = getParticipantsHash(participant1, participant2);

        require(participants_hash_to_channel_identifier[pair_hash] == 0);
        participants_hash_to_channel_identifier[pair_hash] = channel_identifier;

        Channel storage channel = channels[channel_identifier];

        assert(channel.settle_block_number == 0);
        assert(channel.state == ChannelState.NonExistent);

        channel.settle_block_number = settle_timeout;
        channel.state = ChannelState.Opened;

        emit ChannelOpened(
            channel_identifier,
            participant1,
            participant2,
            settle_timeout
        );

        return channel_identifier;
    }

    // function getChannel(address index) public view returns (uint256) {
    //     return channels[1].participants[index].deposit;
    // }



    function setTotalDeposit(
        uint256 channel_identifier,
        address participant,
        uint256 total_deposit,
        address partner
    )
        public
        // isSafe
        isOpen(channel_identifier)
    {
        require(channel_identifier == getChannelIdentifier(participant, partner));
        require(total_deposit > 0);
        require(total_deposit <= channel_participant_deposit_limit);

        uint256 added_deposit;
        uint256 channel_deposit;

        Channel storage channel = channels[channel_identifier];
        Participant storage participant_state = channel.participants[participant];
        Participant storage partner_state = channel.participants[partner];

        added_deposit = total_deposit - participant_state.deposit;

        require(added_deposit > 0);
        require(added_deposit <= total_deposit);

        assert(participant_state.deposit + added_deposit == total_deposit);

        // require(token.balanceOf(address(this)) + added_deposit <= token_network_deposit_limit);

        participant_state.deposit = total_deposit;

        channel_deposit = participant_state.deposit + partner_state.deposit;
        require(channel_deposit >= participant_state.deposit);

        emit ChannelNewDeposit(
            channel_identifier,
            participant,
            participant_state.deposit
        );

        // require(token.transferFrom(msg.sender, address(this), added_deposit));
    }



    function getParticipantsHash(address participant, address partner)
        public
        pure
        returns (bytes32)
    {
        require(participant != address(0x0));
        require(partner != address(0x0));
        require(participant != partner);

        if (participant < partner) {
            return keccak256(abi.encodePacked(participant, partner));
        } else {
            return keccak256(abi.encodePacked(partner, participant));
        }
    }

    function getChannelIdentifier(address participant, address partner)
        public
        view
        returns (uint256)
    {
        require(participant != address(0x0));
        require(partner != address(0x0));
        require(participant != partner);

        bytes32 pair_hash = getParticipantsHash(participant, partner);
        return participants_hash_to_channel_identifier[pair_hash];
    }

    function getChannelInfo(
        uint256 channel_identifier,
        address participant1,
        address participant2
    )
        external
        view
        returns (uint256, ChannelState)
    {
        bytes32 unlock_key1;
        bytes32 unlock_key2;

        Channel storage channel = channels[channel_identifier];
        ChannelState state = channel.state;  // This must **not** update the storage

        if (state == ChannelState.NonExistent &&
            channel_identifier > 0 &&
            channel_identifier <= channel_counter
        ) {
            state = ChannelState.Settled;

            unlock_key1 = getUnlockIdentifier(channel_identifier, participant1, participant2);
            UnlockData storage unlock_data1 = unlock_identifier_to_unlock_data[unlock_key1];

            unlock_key2 = getUnlockIdentifier(channel_identifier, participant2, participant1);
            UnlockData storage unlock_data2 = unlock_identifier_to_unlock_data[unlock_key2];

            if (unlock_data1.locked_amount == 0 && unlock_data2.locked_amount == 0) {
                state = ChannelState.Removed;
            }
        }

        return (
            channel.settle_block_number,
            state
        );
    }

     function getChannelParticipantInfo(
            uint256 channel_identifier,
            address participant,
            address partner
    )
        external
        view
        returns (uint256, uint256, bool, bytes32, uint256, bytes32, uint256)
    {
        bytes32 unlock_key;

        Participant storage participant_state = channels[channel_identifier].participants[
            participant
        ];
        unlock_key = getUnlockIdentifier(channel_identifier, participant, partner);
        UnlockData storage unlock_data = unlock_identifier_to_unlock_data[unlock_key];

        return (
            participant_state.deposit,
            participant_state.withdrawn_amount,
            participant_state.is_the_closer,
            participant_state.balance_hash,
            participant_state.nonce,
            unlock_data.locksroot,
            unlock_data.locked_amount
        );
    }

    function getUnlockIdentifier(
        uint256 channel_identifier,
        address sender,
        address receiver
    )
        public
        pure
        returns (bytes32)
    {
        require(sender != receiver);
        return keccak256(abi.encodePacked(channel_identifier, sender, receiver));
    }
}