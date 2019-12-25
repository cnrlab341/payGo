function calculateLockedAmount (
        // get from leaf included in rocksroot.
        uint256 locked_amount, uint256 expiration, bytes32 secrethash, address target, uint256 start_time,
        uint256 selected_incentive, uint256 selected_delay, uint256 aux_incentive, uint256 aux_delay)
        view internal returns(uint256) {

        uint256 reveal_time;
        uint256 end_time;
        uint256 final_incentive;
        uint256 final_delay;

        reveal_time = secret_registry.getSecretRevealTime(secrethash, target);
        if (reveal_time == 0 || expiration <= reveal_time) {
            locked_amount = 0;
        }
        else {
            end_time = secret_registry.getEndtime(secrethash, target);
            final_delay = end_time-start_time;
            if (selected_delay >= final_delay) {
                final_incentive = selected_incentive;
            }
            else if (aux_delay >= final_delay){
                final_incentive = aux_incentive;
            }
            locked_amount = locked_amount - selected_incentive + final_incentive;
        }
        return locked_amount;
    }