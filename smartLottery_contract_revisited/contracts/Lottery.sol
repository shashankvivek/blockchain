// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

//what is payable type ?


contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;
    uint256 public fee;
    bytes32 public keyHash;
    address payable public recentWinner;
    uint256 public randomness;
    event RequestedRandomness(bytes32 requestId);

    constructor (
        address _priceFeed,
        address _vrfCordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash) 
        public 
        VRFConsumerBase(_vrfCordinator,_link){
        usdEntryFee = 50 *(10**18);
        ethUsdPriceFeed =  AggregatorV3Interface(_priceFeed);
        lottery_state = LOTTERY_STATE.CLOSED;
        keyHash = _keyHash; 
    }


    function enter() public payable{
        require(lottery_state == LOTTERY_STATE.OPEN,"Lottery not yet started");
        require(msg.value >= getEntranceFee(),"Not Enough ETH to enter the game !");
        players.push(msg.sender);
    }

    // To convert and check - how much they are sending is 50$
    // 50$ approx 0.014 ETH => 140000000000000000 WEI.
    // it returns 50$ in WEI
    function getEntranceFee() public view returns (uint256){
        (
            /*uint80 roundID*/,
            int256 price,
            /*uint startedAt*/,
            /*uint timeStamp*/,
            /*uint80 answeredInRound*/
        ) = ethUsdPriceFeed.latestRoundData(); // price of 1 ETH in USD
        uint256 adjustedPrice = uint256(price) * (10**10); // converting the value 10 18 decimals
        uint256 costToEnter = (usdEntryFee * 10**18)/adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner{
        require(lottery_state == LOTTERY_STATE.CLOSED,"Cant start the lottery");
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash,fee);
        emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 requestId, uint256 _randomness) internal override {
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER,"You are not there yet");
        require(_randomness > 0 ,"random_not_found");
        uint256 indexOfWinner = _randomness % players.length;
        recentWinner = players[indexOfWinner];
        recentWinner.transfer(address(this).balance);
        //Reset
        players = new address payable[](0);
        lottery_state = LOTTERY_STATE.CLOSED;
        randomness = randomness;
    }
}